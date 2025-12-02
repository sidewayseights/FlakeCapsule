import json, time, pathlib
class EvidenceLog:
    def __init__(self, path: str):
        self.path = pathlib.Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = self.path.open('a', encoding='utf-8')
    def write(self, event: str, **kv):
        rec = {'ts': time.time(), 'event': event, **kv}
        self.f.write(json.dumps(rec) + '\n'); self.f.flush()
    def close(self):
        try: self.f.close()
        except: pass
