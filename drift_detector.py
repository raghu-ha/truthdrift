"""
TruthDrift - Drift Detector
Compares current state of a wiki article against its last snapshot.
Flags what has changed and how severely.
"""

import json
from pathlib import Path
from snapshot import snapshot_article
from duckdb_store import get_latest_snapshot, save_snapshot, init_db


def detect_drift(filepath: str) -> dict:
    """
    Compare current article state against last snapshot.
    Returns a drift report.
    """
    # Take current snapshot
    current = snapshot_article(filepath)

    # Get last stored snapshot
    previous = get_latest_snapshot(str(Path(filepath).resolve()))

    if previous is None:
        print(f"⚠️  No previous snapshot found for {filepath}")
        print("📸 Saving first snapshot now...")
        save_snapshot(current)
        return {
            "status": "FIRST_SNAPSHOT",
            "message": "No previous snapshot. Baseline captured.",
            "filepath": filepath
        }

    # Unpack previous snapshot
    prev_hash       = previous[4]
    prev_words      = previous[5]
    prev_lines      = previous[6]
    prev_chars      = previous[7]
    prev_backlinks  = previous[8]
    prev_captured   = previous[3]

    # Compare
    hash_changed    = current["content_hash"] != prev_hash
    word_delta      = current["word_count"] - prev_words
    line_delta      = current["line_count"] - prev_lines
    char_delta      = current["char_count"] - prev_chars
    backlink_delta  = current["backlink_count"] - previous[8] if isinstance(previous[8], int) else 0

    # Severity scoring
    if not hash_changed:
        severity = "NONE"
        status = "✅ NO DRIFT"
    elif abs(word_delta) < 20:
        severity = "LOW"
        status = "🔵 MINOR DRIFT"
    elif abs(word_delta) < 100:
        severity = "MEDIUM"
        status = "🟡 MODERATE DRIFT"
    else:
        severity = "HIGH"
        status = "🔴 SIGNIFICANT DRIFT"

    report = {
        "status": status,
        "severity": severity,
        "filepath": filepath,
        "filename": current["filename"],
        "previous_snapshot": prev_captured,
        "current_snapshot": current["captured_at"],
        "hash_changed": hash_changed,
        "word_delta": word_delta,
        "line_delta": line_delta,
        "char_delta": char_delta,
        "previous_words": prev_words,
        "current_words": current["word_count"],
    }

    # Save new snapshot
    if hash_changed:
        save_snapshot(current)
        print(f"📸 New snapshot saved for {current['filename']}")

    return report


def print_report(report: dict):
    print("\n" + "="*50)
    print(f"  TruthDrift Report")
    print("="*50)
    print(f"  File     : {report['filename']}")
    print(f"  Status   : {report['status']}")
    print(f"  Severity : {report.get('severity', 'N/A')}")
    if report.get("hash_changed"):
        print(f"  Words    : {report['previous_words']} → {report['current_words']} ({report['word_delta']:+d})")
        print(f"  Lines    : {report.get('line_delta', 0):+d}")
        print(f"  Chars    : {report.get('char_delta', 0):+d}")
    print(f"  Captured : {report.get('current_snapshot', 'N/A')}")
    print("="*50 + "\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 drift_detector.py <path-to-wiki-article>")
        sys.exit(1)

    init_db()
    report = detect_drift(sys.argv[1])
    print_report(report)
