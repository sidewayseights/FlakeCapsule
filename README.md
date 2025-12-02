# FlakeCapsule — Flaky Test Automator (v0.2)

> Detects flaky tests, **minimizes** reproduction conditions, and **packages deterministic replay capsules** with integrity hashes.  
> Outcome: **MTTR 4–8 hours → <30 minutes** for common timing/order-dependent failures.

---

## Why this matters
Flaky tests waste engineering time, block deploys, and erode trust in CI. FlakeCapsule gives teams a **repeatable, shareable repro** with evidence so fixes land faster.

- **Detect**: Identify non-deterministic failures across runs.
- **Minimize**: Reduce the failure to a small set of critical conditions (e.g., timing jitter, test order).
- **Package**: Emit a portable **capsule**: `stats.json` + `evidence/` + `replay.py` (with SHA-256 signature).
- **Replay**: Deterministic reproduction from the capsule—locally or in CI.

---

## Quickstart

### 1) Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run the sample flaky tests
```bash
pytest -q examples
```

### 3) Detect + Minimize + Package (one-line CLI)
```bash
python -m flakecapsule.cli detect --path examples --out out/capsule   && python -m flakecapsule.cli minimize --capsule out/capsule   && python -m flakecapsule.cli package --capsule out/capsule --out out/FlakeCapsule_v0_2.zip
```

> **Tip:** If your Python can’t find the module, run from repo root and use `python -m flakecapsule.cli ...`.  
> Each subcommand also has its own module (see `detector.py`, `minimizer.py`, `packager.py`).

### 4) Deterministic replay
```bash
python out/capsule/replay.py
```

This will run with the same minimized conditions used to reproduce the failure and print a verification that the **SHA-256** matches the original capsule.

---

## What’s inside the capsule
```
out/capsule/
├─ stats.json          # runs, failure signatures, minimization summary
├─ evidence/           # logs, seed values, timing/order traces
├─ replay.py           # deterministic reproduction script
└─ signature.txt       # SHA-256 of the bundle
```

---

## Repo structure
```
flakecapsule/
├─ __init__.py
├─ cli.py              # small CLI wrapper around the steps below
├─ detector.py         # finds non-deterministic failures across multiple runs
├─ minimizer.py        # reduces timing/order space (ddmin-style)
├─ packager.py         # writes capsule (stats/evidence/replay/signature)
├─ evidence.py         # evidence collection helpers
├─ util.py             # shared utils (seeds, hashing, fs helpers)
└─ ci_entrypoint.py    # example CI entrypoint (GitHub Actions)
examples/
├─ flaky_time_test.py  # timing-dependent example
└─ flaky_order_test.py # order-dependent example
requirements.txt
README.md
LICENSE
```

---

## CI / GitHub Actions
A basic workflow is included (`.github/workflows/ci.yml`). It demonstrates running examples and attaching the exported capsule as a build artifact.  
If you don’t need CI yet, delete or disable the workflow.

---

## Roadmap
- [ ] Heuristics for async/network-related flakiness
- [ ] Rich HTML report (with charts)
- [ ] Capsule schema v0.3 (signing + verification API)
- [ ] Language adapters (Jest/JUnit)
- [ ] PyPI packaging

---

## FAQ

**Is this production-ready?**  
This is a public **demo build (v0.2)** to show the approach. The CLI and capsule format are stable enough for demos and experimentation.

**Why MTTR “4–8h → <30m”?**  
Across common timing/order flake classes, teams often spend hours reproducing and sharing evidence. Automating detection, minimization, and packaging shortens that path substantially.

**Will it work with my tests?**  
Start with the examples. If your suite uses `pytest`, point `--path` to your tests and iterate with the minimizer flags.

---

## License
MIT — see `LICENSE`.

## Contact
Questions or ideas? Open an issue or start a discussion.
