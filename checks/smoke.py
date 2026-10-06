"""Check an initialized local deployment without making provider calls."""
import json,urllib.request,urllib.error,http.cookiejar
from pathlib import Path
root=Path(__file__).resolve().parents[1]
env=dict(l.split('=',1) for l in (root/'.local/installation.env').read_text().splitlines() if '=' in l and not l.startswith('#'))
proxy='http://127.0.0.1:'+env.get('PROXY_PORT','4000');dash='http://127.0.0.1:'+env.get('DASHBOARD_PORT','3000')
def get(url,headers=None):
 with urllib.request.urlopen(urllib.request.Request(url,headers=headers or {}),timeout=20) as r:return json.load(r)
h=get(proxy+'/health')
assert h['license']['required'] is True and h['license']['allowed'] is True
assert h['mode']=='strict' and h['bounded_admission']['accounting_authority']=='postgres'
assert h['bounded_admission']['profile_validity']['ready']
orgs=get(proxy+'/internal/orgs',{'Authorization':'Bearer '+env['LITELLM_MASTER_KEY']})
assert len(orgs)==1 and orgs[0]['id']=='community'
try:get(dash+'/api/overview')
except urllib.error.HTTPError as e:assert e.code in (401,403)
else:raise AssertionError('Unauthenticated dashboard access was accepted')
jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
req=urllib.request.Request(dash+'/api/login',data=json.dumps({'username':'admin','password':env['ADMIN_PASSWORD']}).encode(),headers={'Content-Type':'application/json','x-tollgate':'1'})
with opener.open(req,timeout=20) as r:assert r.status==200
with opener.open(dash+'/api/me',timeout=20) as r:assert json.load(r)['authed']
print(json.dumps({'strict_postgres':True,'offline_signed_entitlement':True,'organization_created':True,'unauthenticated_dashboard_denied':True,'dashboard_login':True,'provider_calls':0}))
