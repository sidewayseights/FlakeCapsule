import os, random, time
def set_seed(seed: int | None):
    if seed is not None:
        random.seed(seed); os.environ['FC_SEED']=str(seed)
def jitter_sleep(base_seconds: float, jitter: float = 0.0):
    if jitter <= 0: time.sleep(base_seconds)
    else:
        delta=(random.random()*2 - 1)*jitter
        delay=max(0.0, base_seconds + delta); time.sleep(delay)
def enable_jitter_env(jitter: float): os.environ['FC_JITTER']=str(jitter)
def enable_shuffle_env(flag: bool): os.environ['FC_SHUFFLE']='1' if flag else '0'
