import os, subprocess, json, pathlib, random, collections
from .evidence import EvidenceLog
from .util import sig_hash

def list_tests(path: str):
    out = subprocess.run(['pytest', path, '--collect-only', '-q'], capture_output=True, text=True, check=False)
    return [ln.strip() for ln in out.stdout.splitlines() if '::' in ln and ' - ' not in ln]

def run_single(nodeid: str, env=None, timeout=120):
    p = subprocess.run(['pytest', nodeid, '-q'], capture_output=True, text=True, timeout=timeout, env=env)
    return p.returncode, p.stdout + p.stderr

def signature_block(text: str) -> str:
    lines = [ln for ln in (text or '').splitlines() if ln.strip()]
    tail = '\n'.join(lines[-5:])
    return tail[-500:]

def detect(path: str, runs: int=20, jitter: float=0.0, shuffle: bool=False, seed: int|None=None, env_kv=None, evidence_path='evidence/evidence.jsonl'):
    env = os.environ.copy()
    if env_kv: env.update(env_kv)
    if seed is not None:
        random.seed(seed); env['FC_SEED']=str(seed)
    env['FC_JITTER']=str(jitter); env['FC_SHUFFLE']='1' if shuffle else '0'

    ev = EvidenceLog(evidence_path)
    path = str(pathlib.Path(path)); tests = list_tests(path)

    results = []; order = tests[:]
    for i in range(runs):
        if shuffle: random.shuffle(order)
        for node in order:
            rc,out = run_single(node, env=env)
            ok = (rc==0)
            sig = None if ok else signature_block(out)
            shash = None if ok else sig_hash(sig or '')
            results.append({'i':i,'node':node,'ok':ok,'sig':sig,'sig_hash':shash})
            ev.write('run', i=i, node=node, ok=ok, sig_hash=shash)

    per_node = collections.defaultdict(lambda: {'pass':0,'fail':0,'sig_hashes':collections.Counter()})
    for r in results:
        if r['ok']: per_node[r['node']]['pass']+=1
        else:
            per_node[r['node']]['fail']+=1
            if r['sig_hash']: per_node[r['node']]['sig_hashes'][r['sig_hash']]+=1

    flakiest = []
    for n,v in per_node.items():
        if v['fail']>0 and v['pass']>0:
            top = v['sig_hashes'].most_common(1)[0][0] if v['sig_hashes'] else None
            flakiest.append({'node':n,'pass':v['pass'],'fail':v['fail'],'sig_hash_top':top,'sig_hash_count':len(v['sig_hashes'])})

    total_runs = len(results); total_fails = sum(1 for r in results if not r['ok'])
    pct_flaky = round((total_fails / total_runs)*100, 2) if total_runs else 0.0

    cap = pathlib.Path('capsule'); cap.mkdir(exist_ok=True)
    stats = {'runs': total_runs, 'fails': total_fails, 'pct_flaky': pct_flaky, 'top_flaky_nodes': flakiest[:5]}
    (cap/'stats.json').write_text(json.dumps(stats, indent=2))

    best = max(flakiest, key=lambda x: x['fail'], default=None)
    meta = {
        'order': tests,
        'env': {'FC_SEED': env.get('FC_SEED'), 'FC_JITTER': env.get('FC_JITTER'), 'FC_SHUFFLE': env.get('FC_SHUFFLE'), **(env_kv or {})},
        'expected_signature_hash': best['sig_hash_top'] if best else None
    }
    (cap/'metadata.json').write_text(json.dumps(meta, indent=2))

    ev.write('summary', flakiest=flakiest, stats=stats); ev.close()
    return {'tests':tests,'flakiest':flakiest,'stats':stats,'metadata':meta}
