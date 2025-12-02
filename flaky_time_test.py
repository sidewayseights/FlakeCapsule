import os, time, random
def jitter_sleep(base=0.01):
    jitter=float(os.environ.get('FC_JITTER','0') or '0')
    delta=(random.random()*2 - 1)*jitter
    time.sleep(max(0.0, base+delta))
def fragile_check():
    t=time.perf_counter(); jitter_sleep(0.01); elapsed=time.perf_counter()-t
    return elapsed >= 0.009
def test_sometimes_flaky_time():
    ok=fragile_check()
    assert ok, f"timing below threshold under jitter={os.environ.get('FC_JITTER')}"
