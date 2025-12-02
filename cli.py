import argparse, json, pathlib
from .detector import detect
from .minimizer import minimize_order, minimize_timing
from .packager import write_capsule

def parse_env_kv(items):
    env={}
    for it in items or []:
        if '=' in it:
            k,v=it.split('=',1); env[k.strip()]=v.strip()
    return env

def main():
    p=argparse.ArgumentParser(prog='flakecapsule')
    sub=p.add_subparsers(dest='cmd', required=True)

    d=sub.add_parser('detect')
    d.add_argument('path'); d.add_argument('--runs',type=int,default=20)
    d.add_argument('--jitter',type=float,default=0.0)
    d.add_argument('--shuffle',type=int,default=0)
    d.add_argument('--seed',type=int,default=None)
    d.add_argument('--env',action='append')

    m=sub.add_parser('minimize-order')
    m.add_argument('path'); m.add_argument('--runs',type=int,default=20)
    m.add_argument('--shuffle',type=int,default=1)
    m.add_argument('--seed',type=int,default=123)
    m.add_argument('--jitter',type=float,default=0.01)
    m.add_argument('--env',action='append')

    t=sub.add_parser('minimize-timing')
    t.add_argument('path'); t.add_argument('--node',default=None)
    t.add_argument('--runs',type=int,default=15)
    t.add_argument('--max-jitter',type=float,default=0.02)
    t.add_argument('--seed',type=int,default=None)
    t.add_argument('--env',action='append')

    k=sub.add_parser('pack'); k.add_argument('--out',default='capsule.zip')

    args=p.parse_args()
    if args.cmd=='detect':
        env=parse_env_kv(args.env)
        res=detect(args.path, runs=args.runs, jitter=args.jitter, shuffle=bool(args.shuffle), seed=args.seed, env_kv=env)
        print(json.dumps(res, indent=2))
    elif args.cmd=='minimize-order':
        env=parse_env_kv(args.env)
        res=minimize_order(args.path, runs=args.runs, shuffle=bool(args.shuffle), seed=args.seed, jitter=args.jitter, extra_env=env)
        print(json.dumps(res, indent=2))
    elif args.cmd=='minimize-timing':
        env=parse_env_kv(args.env)
        res=minimize_timing(args.path, node=args.node, runs=args.runs, max_jitter=args.max_jitter, seed=args.seed, extra_env=env)
        print(json.dumps(res, indent=2))
    elif args.cmd=='pack':
        out=write_capsule(out_zip=args.out)
        print(json.dumps({'out':out}, indent=2))

if __name__=='__main__': main()
