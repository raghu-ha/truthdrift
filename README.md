# TruthDrift 🔍

> **Context Integrity Monitor for LLM Knowledge Systems**

Built on Andrej Karpathy's LLM Wiki pattern (April 2026).

---

## The Problem

You build a wiki. An LLM compiles your documents into structured knowledge articles.
You query it. You get answers.

But tomorrow — the source data changes.

The wiki article is now stale. The answer it gives is based on yesterday's reality.
**Nobody knows.**

TruthDrift fixes that.

---

## What It Does

```
Wiki article created
        ↓
TruthDrift captures fingerprint (hash + stats + timestamp)
        ↓
Stored in DuckDB locally
        ↓
Tomorrow — article changes
        ↓
TruthDrift detects drift
        ↓
Flags severity: 🔵 LOW | 🟡 MEDIUM | 🔴 HIGH
        ↓
You know exactly what drifted and when
```

---

## Architecture

```
truthdrift/
├── snapshot.py        → captures article fingerprint
├── duckdb_store.py    → stores snapshots in DuckDB
├── drift_detector.py  → compares current vs snapshot
├── truthdrift.py      → main CLI
└── truthdrift.db      → local DuckDB (auto-created)
```

---

## Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install duckdb

# Capture baseline snapshot
python3 truthdrift.py snapshot ~/raghu-wiki/wiki/pages/truthdrift.md

# Check for drift (run again after editing the article)
python3 truthdrift.py check ~/raghu-wiki/wiki/pages/truthdrift.md

# Check entire wiki at once
python3 truthdrift.py check-all ~/raghu-wiki/wiki/pages/

# List all snapshots
python3 truthdrift.py list
```

---

## Sample Output

```
==================================================
  TruthDrift Report
==================================================
  File     : truthdrift.md
  Status   : 🔴 SIGNIFICANT DRIFT
  Severity : HIGH
  Words    : 312 → 489 (+177)
  Lines    : +23
  Chars    : +1,043
  Captured : 2026-04-07T18:32:11
==================================================
```

---

## Use Cases

| Domain | How TruthDrift helps |
|---|---|
| **Personal Wiki** | Know when compiled knowledge drifts from source docs |
| **DQ Automation** | Detect when DQ rules go stale after schema changes |
| **Governance** | Flag when policy articles drift from actual policy docs |
| **Enterprise KB** | Monitor institutional knowledge for staleness |

---

## The Insight

> *"RAG rediscovers knowledge from scratch every time.*
> *The wiki compiles it once — but compiled knowledge can go stale.*
> *TruthDrift is the integrity layer the wiki pattern was missing."*

---

## Built With

- Python 3.12
- DuckDB (embedded, zero infra)
- Markdown (plain files, no lock-in)

---

## Author

**Raghavendra** — Data Engineering & Solution Architecture @ Deloitte India

Inspired by Andrej Karpathy's LLM Wiki pattern:
gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

---

## License

MIT — use it, fork it, build on it.
