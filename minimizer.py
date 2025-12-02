import os, random, subprocess, json, math, pathlib
from .detector import list_tests
from .util import sig_hash

def run_sequence(nodes, env, timeout=120):
    last_out=None
    for node in nodes:
        p=subprocess.run(['pytest', node, '-q'], capture_output=True, text=True, timeout=timeout, env=env)
        if p.returncode!=0:
            last_out=p.stdout+p.stderr; return True, last_out
    return False, last_out

def ddmin_order(all_nodes, env, max_iters=50):
    n=2; seq=list(all_nodes); iters=0
    while len(seq)>1 and iters<max_iters:
        iters+=1; chunk=math.ceil(len(seq)/n); reduced=False
        for i in range(0,len(seq),chunk):
            cand=seq[:i]+seq[i+chunk:]
            if not cand: continue
            ok,_=run_sequence(cand, env)
            if ok:
                seq=cand; n=max(n-1,2); reduced=True; break
        if not reduced:
            if n>=len(seq): break
            n=min(len(seq), n*2)
    return seq

def minimize_order(path, runs=20, shuffle=True, seed=None, jitter=0.01, extra_env=None):
    env=os.environ.copy()
    if extra_env: env.update(extra_env)
    if seed is not None:
        env['FC_SEED']=str(seed); random.seed(seed)
    env['FC_JITTER']=str(jitter); env['FC_SHUFFLE']='1' if shuffle else '0'

    nodes=list_tests(path)
    if shuffle: random.shuffle(nodes)

    ok,out=run_sequence(nodes, env)
    if not ok: return {'ok':False,'reason':'No failing sequence found under current perturbations'}

    minimized=ddmin_order(nodes, env)
    cap=pathlib.Path('capsule'); cap.mkdir(exist_ok=True)
    meta=json.loads((cap/'metadata.json').read_text()) if (cap/'metadata.json').exists() else {'order':minimized,'env':env}
    meta['order']=minimized; meta.setdefault('env',{}).update(env)
    if out: meta['expected_signature_hash']=sig_hash(out[-500:])
    (cap/'metadata.json').write_text(json.dumps(meta, indent=2))
    return {'ok':True,'minimized':minimized,'env':{'FC_SEED':env.get('FC_SEED'),'FC_JITTER':env.get('FC_JITTER'),'FC_SHUFFLE':env.get('FC_SHUFFLE')}}

def minimize_timing(path, node=None, runs=15, max_jitter=0.02, seed=None, extra_env=None):
    import subprocess
    env=os.environ.copy()
    if extra_env: env.update(extra_env)
    if seed is not None: env['FC_SEED']=str(seed); random.seed(seed)
    nodes=list_tests(path)
    if node is None and nodes: node=nodes[0]

    def fails_at(j):
        env['FC_JITTER']=str(j); env['FC_SHUFFLE']='0'
        for _ in range(runs):
            p=subprocess.run(['pytest', node, '-q'], capture_output=True, text=True, env=env)
            if p.returncode!=0:
                return True, p.stdout+p.stderr
        return False, None

    low, high = 0.0, max_jitter
    ok,out = fails_at(high)
    if not ok: return {'ok':False,'reason':f'No failure at max_jitter={max_jitter}. Increase and retry.', 'node':node}
    last_out=out
    for _ in range(12):
        mid=(low+high)/2
        ok,out=fails_at(mid)
        if ok: high=mid; last_out=out
        else: low=mid

    cap=pathlib.Path('capsule'); cap.mkdir(exist_ok=True)
    meta=json.loads((cap/'metadata.json').read_text()) if (cap/'metadata.json').exists() else {'order':[node],'env':{}}
    meta['env']['FC_JITTER']=str(high)
    if last_out: meta['expected_signature_hash']=sig_hash(last_out[-500:])
    (cap/'metadata.json').write_text(json.dumps(meta, indent=2))
    return {'ok':True,'node':node,'min_jitter':high}
