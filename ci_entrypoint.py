import os, json
from .detector import detect
from .packager import write_capsule
def main():
    path=os.environ.get('FC_PATH','.');
    runs=int(os.environ.get('FC_RUNS','20'))
    jitter=float(os.environ.get('FC_JITTER','0.015'))
    shuffle=os.environ.get('FC_SHUFFLE','0')=='1'
    seed=int(os.environ.get('FC_SEED')) if os.environ.get('FC_SEED') else None
    extra_env={k[7:]:v for k,v in os.environ.items() if k.startswith('FC_ENV_')}
    res=detect(path, runs=runs, jitter=jitter, shuffle=shuffle, seed=seed, env_kv=extra_env)
    out=write_capsule()
    print(json.dumps({'stats':res['stats'], 'metadata':res['metadata'], 'out':out}, indent=2))
if __name__=='__main__': main()
