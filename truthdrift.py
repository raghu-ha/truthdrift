"""
TruthDrift - Main CLI
Context Integrity Monitor for LLM Knowledge Systems.

Usage:
  python3 truthdrift.py snapshot <article>   → capture baseline
  python3 truthdrift.py check <article>      → detect drift
  python3 truthdrift.py list                 → show all snapshots
  python3 truthdrift.py check-all <wiki-dir> → check entire wiki
"""

import sys
from pathlib import Path
from duckdb_store import init_db, list_all_snapshots
from snapshot import snapshot_article
from duckdb_store import save_snapshot
from drift_detector import detect_drift, print_report


def cmd_snapshot(filepath):
    init_db()
    snap = snapshot_article(filepath)
    save_snapshot(snap)
    print(f"\n📸 Snapshot captured for {snap['filename']}")
    print(f"   Hash  : {snap['content_hash'][:16]}...")
    print(f"   Words : {snap['word_count']}")
    print(f"   Time  : {snap['captured_at']}")


def cmd_check(filepath):
    init_db()
    report = detect_drift(filepath)
    print_report(report)


def cmd_list():
    init_db()
    snaps = list_all_snapshots()
    if not snaps:
        print("No snapshots yet. Run: python3 truthdrift.py snapshot <article>")
        return
    print(f"\n📋 TruthDrift Snapshot History ({len(snaps)} total)")
    print("-" * 60)
    for s in snaps:
        print(f"  {s[0]:<30} | {s[1][:19]} | words: {s[3]}")
    print("-" * 60)


def cmd_check_all(wiki_dir):
    """Check all markdown files in a wiki directory for drift."""
    init_db()
    wiki_path = Path(wiki_dir)
    articles = list(wiki_path.rglob("*.md"))

    if not articles:
        print(f"No markdown files found in {wiki_dir}")
        return

    print(f"\n🔍 Checking {len(articles)} articles for drift...\n")

    drifted = []
    clean = []

    for article in articles:
        report = detect_drift(str(article))
        if report.get("severity") in ("LOW", "MEDIUM", "HIGH"):
            drifted.append(report)
        elif report.get("status") != "FIRST_SNAPSHOT":
            clean.append(report)

    print("\n" + "="*50)
    print(f"  TruthDrift Wiki Health Report")
    print("="*50)
    print(f"  ✅ Clean    : {len(clean)} articles")
    print(f"  ⚠️  Drifted  : {len(drifted)} articles")
    print(f"  📸 New      : {len(articles) - len(drifted) - len(clean)} articles")

    if drifted:
        print("\n  🔴 Drifted articles:")
        for r in drifted:
            print(f"    → {r['filename']} [{r['severity']}] ({r['word_delta']:+d} words)")
    print("="*50 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "snapshot" and len(sys.argv) == 3:
        cmd_snapshot(sys.argv[2])
    elif cmd == "check" and len(sys.argv) == 3:
        cmd_check(sys.argv[2])
    elif cmd == "list":
        cmd_list()
    elif cmd == "check-all" and len(sys.argv) == 3:
        cmd_check_all(sys.argv[2])
    else:
        print(__doc__)
