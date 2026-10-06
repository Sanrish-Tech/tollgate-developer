#!/usr/bin/env python3
"""Quiesced customer installation backup. Output contains secrets: keep private."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('installation', type=Path)
    p.add_argument('destination', type=Path)
    p.add_argument('--project', default='tollgate-developer')
    p.add_argument('--verify-restore', action='store_true', help='Restore to a disposable database and compare every table while apps are stopped')
    a = p.parse_args()
    root = a.installation.resolve()
    out = a.destination.resolve()
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    compose = ['docker', 'compose', '-p', a.project, '--env-file', str(root/'.local/installation.env'), '-f', str(root/'compose.yml')]
    def run(*args, **kwargs):
        return subprocess.run(compose + list(args), check=True, stderr=subprocess.PIPE, **kwargs)
    # Preserve the running set: maintenance must not start a previously stopped
    # service or use a changed manifest while resuming the existing containers.
    running = run('ps', '--services', '--status', 'running', stdout=subprocess.PIPE).stdout.decode().split()
    apps = [s for s in ('dashboard', 'proxy', 'gateway') if s in running]
    try:
        if apps: run('stop', *apps, stdout=subprocess.DEVNULL)
        with os.fdopen(os.open(out/'database.dump', os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600), 'wb') as f:
            run('exec', '-T', 'db', 'sh', '-c', 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-acl', stdout=f)
        # Copy state from the existing stopped container, without starting an
        # image or injecting credentials into a backup utility container.
        state = out/'dashboard-state'
        state.mkdir(mode=0o700)
        run('cp', 'dashboard:/data/.', str(state), stdout=subprocess.DEVNULL)
        for name in ('.local/installation.env', '.local/provider.env', 'compose.yml', 'distribution/gateway.yaml', 'distribution/direct-profiles.json', 'distribution/developer-license.json'):
            target=out/name
            target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            shutil.copyfile(root/name,target)
            os.chmod(target,0o600)
        if a.verify_restore:
            restored = 'tg_restore_' + uuid.uuid4().hex
            def sql(db, query):
                return run('exec','-T','db','psql','-U','tollgate','-d',db,'-At','-c',query,stdout=subprocess.PIPE).stdout.decode().strip()
            def fingerprint(db):
                tables=sql(db,"SELECT quote_ident(schemaname)||'.'||quote_ident(tablename) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY 1").splitlines()
                return {table: sql(db,"SELECT count(*)||':'||coalesce(md5(string_agg(row_to_json(t)::text,E'\\n' ORDER BY row_to_json(t)::text)),'empty') FROM "+table+' t') for table in tables}
            original=fingerprint('tollgate')
            run('exec','-T','db','createdb','-U','tollgate',restored,stdout=subprocess.DEVNULL)
            try:
                with (out/'database.dump').open('rb') as f:
                    run('exec','-T','db','pg_restore','-U','tollgate','-d',restored,'--no-owner','--no-acl','--exit-on-error',stdin=f,stdout=subprocess.DEVNULL)
                recovered=fingerprint(restored)
                if recovered!=original: raise ValueError('Restored database contents differ')
                (out/'restore-verification.json').write_text(json.dumps({'passed':True,'matching_tables':len(original)}))
            finally:
                run('exec','-T','db','dropdb','-U','tollgate',restored,stdout=subprocess.DEVNULL)
        files = {str(f.relative_to(out)): hashlib.sha256(f.read_bytes()).hexdigest()
                 for f in out.rglob('*') if f.is_file()}
        (out/'sha256.json').write_text(json.dumps(files, indent=2))
        os.chmod(out/'sha256.json', 0o600)
    finally:
        if apps: run('start', *apps, stdout=subprocess.DEVNULL)
    print('Quiesced database, account/alert state, configuration backup complete.')
    print('Verify the checksums and a disposable database restore before relying on this backup.')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError:
        raise SystemExit('Backup command failed. Existing services were scheduled to resume; inspect their health. No captured credentials printed.')
