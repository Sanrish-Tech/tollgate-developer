#!/usr/bin/env python3
"""Create local credentials without activation or provider calls."""
import os,secrets
from pathlib import Path
root=Path(__file__).resolve().parent
local=root/'.local'
if local.exists():raise SystemExit('.local already exists; preserving credentials and data. No changes made.')
local.mkdir(mode=0o700)
values={'POSTGRES_PASSWORD':secrets.token_hex(32),'LITELLM_MASTER_KEY':'sk-'+secrets.token_hex(32),'ADMIN_PASSWORD':secrets.token_urlsafe(24),'SESSION_SECRET':secrets.token_hex(32),'LICENSED_ORG':'community','PROXY_PORT':'4000','DASHBOARD_PORT':'3000'}
for name,body in [('installation.env',''.join(f'{k}={v}\n' for k,v in values.items())),('provider.env','# Set your own provider keys here. Only the proxy receives them.\nOPENAI_API_KEY=\nANTHROPIC_API_KEY=\n')]:
 with os.fdopen(os.open(local/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:f.write(body)
print('Local installation prepared. Credentials are in .local/installation.env (not printed).')
print('Set your provider key in .local/provider.env, then follow README.md.')
