#!/usr/bin/env python3
"""Verify and atomically install a signed TollGate profile catalogue bundle."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import tempfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DOMAIN = b"TollGate model catalogue manifest v1\n"
MAX_FILE = 16 * 1024 * 1024


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def read(path, limit=MAX_FILE):
    with Path(path).open("rb") as stream:
        value = stream.read(limit + 1)
    if len(value) > limit:
        raise ValueError("catalogue update file is too large")
    return value


def load_json(path):
    return json.loads(read(path), object_pairs_hook=unique)


def validate_profiles(value):
    if not isinstance(value, dict) or set(value) != {"version", "transport", "profiles"}:
        raise ValueError("profile payload has unexpected fields")
    expected_versions = {"native-direct-api": 1, "native-bedrock-converse": 2}
    if value["transport"] not in expected_versions or value["version"] != expected_versions[value["transport"]]:
        raise ValueError("unsupported profile payload")
    if not isinstance(value["profiles"], list) or not value["profiles"]:
        raise ValueError("profile payload is empty")
    aliases = set()
    for profile in value["profiles"]:
        required = {"status", "alias", "target", "input_token_ceiling", "max_output_tokens",
                    "input_usd_per_token", "output_usd_per_token", "per_request_usd",
                    "valid_from", "expires_on", "reviewed_by", "evidence"}
        if not isinstance(profile, dict) or not required <= set(profile):
            raise ValueError("profile is incomplete")
        if (not isinstance(profile["alias"], str) or not profile["alias"]
                or not isinstance(profile["target"], str) or not profile["target"]
                or profile["alias"] in aliases
                or profile["status"] not in {"candidate", "approved", "retiring"}):
            raise ValueError("profile alias or status is invalid")
        aliases.add(profile["alias"])
        if (type(profile["input_token_ceiling"]) is not int or profile["input_token_ceiling"] <= 0
                or type(profile["max_output_tokens"]) is not int or profile["max_output_tokens"] <= 0):
            raise ValueError("profile token limits must be integers")
        start = datetime.fromisoformat(profile["valid_from"])
        end = datetime.fromisoformat(profile["expires_on"])
        if end < start or not profile["evidence"].startswith("https://") or not profile["reviewed_by"].strip():
            raise ValueError("profile review window or evidence is invalid")
        for field in ("input_usd_per_token", "output_usd_per_token", "per_request_usd"):
            try:
                amount = Decimal(profile[field]) if isinstance(profile[field], str) else None
            except InvalidOperation:
                amount = None
            if amount is None or not amount.is_finite() or amount < 0:
                raise ValueError("profile price is invalid")
    return value


def verify_bundle(bundle, keys):
    bundle = Path(bundle)
    raw_manifest = read(bundle / "manifest.json")
    manifest = json.loads(raw_manifest, object_pairs_hook=unique)
    signature = load_json(bundle / "manifest.signature.json")
    ring = load_json(keys)
    expected_manifest = {"version", "catalogue_version", "previous_catalogue_version", "created_at",
                         "channel", "profiles_sha256", "profiles_size", "profile_count"}
    if set(manifest) != expected_manifest or manifest["version"] != 1:
        raise ValueError("unsupported catalogue manifest")
    if (type(manifest["catalogue_version"]) is not int or manifest["catalogue_version"] < 1
            or (manifest["previous_catalogue_version"] is not None
                and type(manifest["previous_catalogue_version"]) is not int)
            or manifest["channel"] not in {"developer", "aws"}):
        raise ValueError("invalid catalogue version or channel")
    if not isinstance(manifest["created_at"], str) or not manifest["created_at"].endswith("Z"):
        raise ValueError("catalogue creation time must be RFC3339 UTC")
    datetime.fromisoformat(manifest["created_at"].removesuffix("Z") + "+00:00")
    if set(signature) != {"version", "key_id", "manifest_sha256", "signature"} or signature["version"] != 1:
        raise ValueError("invalid signature envelope")
    if hashlib.sha256(raw_manifest).hexdigest() != signature["manifest_sha256"]:
        raise ValueError("manifest digest mismatch")
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(ring[signature["key_id"]], validate=True))
    public.verify(base64.b64decode(signature["signature"], validate=True), DOMAIN + raw_manifest)
    raw_profiles = read(bundle / "profiles.json")
    if len(raw_profiles) != manifest["profiles_size"] or hashlib.sha256(raw_profiles).hexdigest() != manifest["profiles_sha256"]:
        raise ValueError("profile payload digest mismatch")
    profiles = validate_profiles(json.loads(raw_profiles, object_pairs_hook=unique))
    if len(profiles["profiles"]) != manifest["profile_count"]:
        raise ValueError("profile count mismatch")
    return manifest, raw_manifest, raw_profiles, read(bundle / "manifest.signature.json")


def atomic_write(path, value, mode=0o644):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def install(bundle, destination, keys, channel, allow_rollback=False):
    manifest, raw_manifest, raw_profiles, raw_signature = verify_bundle(bundle, keys)
    if manifest["channel"] != channel:
        raise ValueError("catalogue channel does not match this installation")
    destination = Path(destination)
    state_path = destination.parent / ".catalogue-state.json"
    state = load_json(state_path) if state_path.exists() else {
        "current_version": 0, "highest_seen_version": 0, "profiles_sha256": None,
    }
    if (set(state) != {"current_version", "highest_seen_version", "profiles_sha256"}
            or type(state["current_version"]) is not int
            or type(state["highest_seen_version"]) is not int
            or state["current_version"] < 0
            or state["highest_seen_version"] < state["current_version"]):
        raise ValueError("installed catalogue state is invalid")
    if destination.exists() and state["profiles_sha256"] is not None:
        if hashlib.sha256(read(destination)).hexdigest() != state["profiles_sha256"]:
            raise ValueError("installed profiles differ from catalogue state")
    current = state["current_version"]
    version = manifest["catalogue_version"]
    if version <= state["highest_seen_version"] and not (allow_rollback and version < current):
        raise ValueError("catalogue update is not newer; explicit verified rollback is required")
    if not allow_rollback and manifest["previous_catalogue_version"] != current:
        raise ValueError("catalogue update does not continue the installed version")

    history = destination.parent / ".catalogue-history" / f"v{version}"
    if allow_rollback:
        if (not history.is_dir()
                or read(history / "manifest.json") != raw_manifest
                or read(history / "manifest.signature.json") != raw_signature
                or read(history / "profiles.json") != raw_profiles):
            raise ValueError("rollback target is not in this installation's verified history")
    history.mkdir(parents=True, exist_ok=True)
    atomic_write(history / "manifest.json", raw_manifest)
    atomic_write(history / "manifest.signature.json", raw_signature)
    atomic_write(history / "profiles.json", raw_profiles)
    atomic_write(destination, raw_profiles)
    new_state = {
        "current_version": version,
        "highest_seen_version": max(state["highest_seen_version"], version),
        "profiles_sha256": hashlib.sha256(raw_profiles).hexdigest(),
    }
    atomic_write(state_path, (json.dumps(new_state, sort_keys=True) + "\n").encode(), 0o600)
    return new_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--keys", required=True, type=Path)
    parser.add_argument("--channel", required=True, choices=("developer", "aws"))
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    try:
        state = install(args.bundle, args.destination, args.keys, args.channel, args.rollback)
    except Exception:
        raise SystemExit("Catalogue update verification failed; installed profiles were not changed.") from None
    print(f"Installed verified catalogue v{state['current_version']} atomically.")


if __name__ == "__main__":
    main()
