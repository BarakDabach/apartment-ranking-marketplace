#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cache", help="Project cache directory")
    ap.add_argument("--verify-source-hashes", action="store_true")
    args = ap.parse_args()

    root = Path(args.cache).expanduser().resolve()
    manifest_path = root / "manifest.json"
    facts_path = root / "derived" / "facts.json"
    errors = []

    if not manifest_path.exists():
        errors.append("manifest.json missing")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            manifest = None
            errors.append(f"manifest.json invalid JSON: {e}")
        if manifest:
            ids = set()
            for src in manifest.get("sources", []):
                sid = src.get("source_id")
                if not sid or sid in ids:
                    errors.append(f"duplicate/missing source_id: {sid}")
                ids.add(sid)
                sha = src.get("sha256", "")
                if len(sha) != 64:
                    errors.append(f"invalid sha256 for {sid}")
                for page in src.get("pages", []):
                    for key in ("markdown_path", "preview_path"):
                        rel = page.get(key)
                        if not rel or not (root / rel).exists():
                            errors.append(f"missing {key} for {sid} page {page.get('page_number')}: {rel}")
                if args.verify_source_hashes:
                    p = Path(src.get("original_path", ""))
                    if not p.exists():
                        errors.append(f"original source missing: {p}")
                    elif sha256_file(p) != sha:
                        errors.append(f"source hash changed: {p}")

    if not facts_path.exists():
        errors.append("derived/facts.json missing")
    else:
        try:
            facts = json.loads(facts_path.read_text(encoding="utf-8"))
            seen = set()
            for f in facts.get("facts", []):
                fid = f.get("fact_id")
                if not fid or fid in seen:
                    errors.append(f"duplicate/missing fact_id: {fid}")
                seen.add(fid)
                if not f.get("evidence"):
                    errors.append(f"fact has no evidence: {fid}")
        except Exception as e:
            errors.append(f"derived/facts.json invalid JSON: {e}")

    if errors:
        print("CACHE INVALID")
        for e in errors:
            print(f"- {e}")
        return 1
    print("CACHE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
