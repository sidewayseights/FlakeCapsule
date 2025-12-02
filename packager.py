import os, json, pathlib, zipfile

def write_capsule(min_seq=None, env=None, out_zip='capsule.zip'):
    cap=pathlib.Path('capsule'); cap.mkdir(exist_ok=True)
    meta_path=cap/'metadata.json'
    if meta_path.exists(): meta=json.loads(meta_path.read_text())
    else: meta={'order':min_seq or [], 'env':env or {}}
    if min_seq: meta['order']=min_seq
    if env: meta.setdefault('env',{}).update(env)
    meta_path.write_text(json.dumps(meta, indent=2))

    replay='''#!/usr/bin/env python3
import os, subprocess, json, sys, pathlib, hashlib
def sig_hash(text: str) -> str:
    tail=(text or '')[-500:]
    return hashlib.sha256(tail.encode('utf-8','ignore')).hexdigest()
HERE=pathlib.Path(__file__).parent
meta=json.loads((HERE/'metadata.json').read_text())
env=os.environ.copy()
for k,v in (meta.get('env') or {}).items():
    if v is not None: env[k]=str(v)
order=meta.get('order') or []
expected=meta.get('expected_signature_hash')
print('== FlakeCapsule Replay ==')
print('Env:', {k:env.get(k) for k in ['FC_SEED','FC_JITTER','FC_SHUFFLE'] if env.get(k)})
print('Order:', order)
print('Expect signature:', expected)
for node in order:
    print('\n# Running', node)
    p=subprocess.run(['pytest', node, '-q'], capture_output=True, text=True, env=env)
    if p.returncode!=0:
        out=p.stdout+p.stderr; shash=sig_hash(out)
        print('Failure signature hash:', shash)
        if expected and expected!=shash:
            print('WARNING: Signature mismatch (expected != observed).')
        print('\n# Failure reproduced.'); sys.exit(1)
print('\n# No failure occurred in the provided sequence.'); sys.exit(0)
'''
    (cap/'replay.py').write_text(replay); os.chmod(cap/'replay.py', 0o755)
    with zipfile.ZipFile(out_zip,'w',zipfile.ZIP_DEFLATED) as z:
        for p in cap.rglob('*'): z.write(p, p.relative_to(cap.parent))
    return str(out_zip)
