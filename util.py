import hashlib
def sig_hash(text: str) -> str:
    tail = (text or '')[-500:]
    return hashlib.sha256(tail.encode('utf-8', errors='ignore')).hexdigest()
