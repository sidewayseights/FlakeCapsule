#!/usr/bin/env python3
import json, os, random, time, sys, platform, pathlib

ROOT = pathlib.Path(__file__).parent.resolve()
CAP = ROOT / "capsule"
CAP.mkdir(exist_ok=True)

MANIFEST = CAP / "manifest.json"
LOG = CAP / "log.txt"
SEED_FILE = CAP / "seed.txt"

def write_capsule(seed:int, status:str, msg:str):
    MANIFEST.write_text(json.dumps({
        "schema": "flakecapsule.demo/0.1",
        "status": status,
        "message": msg,
        "seed": seed,
        "env": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    }, indent=2))
    SEED_FILE.write_text(str(seed))
    with LOG.open("a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] status={status} message={msg} seed={seed}\n")

def flaky_test(seed:int)->None:
    random.seed(seed)
    time.sleep(0.2)
    # 40% failure on purpose to simulate a flaky test
    if random.random() < 0.4:
        raise AssertionError("Intermittent failure (simulated)")

def run_once(seed=None)->int:
    if seed is None:
        seed = int(time.time()) % 10_000_000
    try:
        flaky_test(seed)
        write_capsule(seed, "pass", "test passed")
        print("✅ PASS")
        return 0
    except AssertionError as e:
        write_capsule(seed, "fail", str(e))
        print("❌ FAIL:", e)
        print("Capsule saved to ./capsule (manifest.json, log.txt, seed.txt)")
        return 1

def cmd_run():
    sys.exit(run_once())

def cmd_replay():
    if not SEED_FILE.exists():
        print("No capsule to replay. Run a failing test first.")
        sys.exit(2)
    seed = int(SEED_FILE.read_text().strip())
    print(f"Replaying with saved seed: {seed}")
    code = run_once(seed)
    if code == 0:
        print("Replay passed; running again to show determinism…")
        code = run_once(seed)
    sys.exit(code)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"run", "replay"}:
        print("Usage: python3 demo_capsule.py [run|replay]")
        sys.exit(2)
    {"run": cmd_run, "replay": cmd_replay}[sys.argv[1]]()
