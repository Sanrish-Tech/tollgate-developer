#!/usr/bin/env python3
"""Create the installation's first budgeted organization without making model calls."""
import argparse
import json
import math
from pathlib import Path
import urllib.request
from zoneinfo import ZoneInfo


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    p.add_argument('--budget', required=True, type=float, help='Organization USD limit for each 30-day window')
    p.add_argument('--name')
    p.add_argument('--timezone', default='UTC')
    a = p.parse_args()
    if not math.isfinite(a.budget) or a.budget < 0:
        p.error('budget must be finite and nonnegative')
    ZoneInfo(a.timezone)
    env = dict(line.split('=', 1) for line in (a.directory/'installation.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
    org = env['LICENSED_ORG']
    port = int(env.get('PROXY_PORT', '4000'))
    if not 1 <= port <= 65535:
        raise ValueError('invalid loopback proxy port')
    url = 'http://127.0.0.1:' + str(port) + '/internal/orgs'
    headers = {'Authorization': 'Bearer ' + env['LITELLM_MASTER_KEY'], 'Content-Type': 'application/json'}
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as response:
        existing = json.load(response)
    if existing:
        if len(existing) != 1 or existing[0]['id'] != org:
            raise ValueError('existing organization differs; inspect instead of replacing')
        print('Installation organization already exists; its budgets and financial state were preserved.')
        return
    body = {'id': org, 'name': a.name or org, 'budget': a.budget, 'budget_duration': '30d', 'timezone': a.timezone}
    # One mutation attempt only. A lost response must be inspected, not replayed.
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers, data=json.dumps(body).encode()), timeout=15) as response:
        result = json.load(response)
    if result.get('id') != org:
        raise ValueError('organization creation could not be confirmed')
    print('Budgeted organization created. Sign in to the dashboard to add a department, project, member and personal key.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        raise SystemExit('Setup could not be confirmed (' + type(exc).__name__ + '). Inspect the dashboard before retrying; no financial state was reset.') from None
