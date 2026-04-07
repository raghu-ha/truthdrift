"""
TruthDrift - Snapshot Engine
Captures a fingerprint of a wiki article at a point in time.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path


def snapshot_article(filepath: str) -> dict:
    """
    Takes a snapshot of a wiki article.
    Returns a fingerprint dict with hash, stats, and timestamp.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Article not found: {filepath}")

    content = path.read_text(encoding="utf-8")

    # Fingerprint
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    word_count = len(content.split())
    line_count = len(content.splitlines())
    char_count = len(content)

    # Extract backlinks (lines with [[...]])
    backlinks = []
    for line in content.splitlines():
        if "[[" in line and "]]" in line:
            start = line.find("[[") + 2
            end = line.find("]]")
            backlinks.append(line[start:end])

    snapshot = {
        "filepath": str(path.resolve()),
        "filename": path.name,
        "captured_at": datetime.utcnow().isoformat(),
        "content_hash": content_hash,
        "word_count": word_count,
        "line_count": line_count,
        "char_count": char_count,
        "backlink_count": len(backlinks),
        "backlinks": backlinks,
    }

    return snapshot


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 snapshot.py <path-to-wiki-article>")
        sys.exit(1)

    snap = snapshot_article(sys.argv[1])
    print(json.dumps(snap, indent=2))
