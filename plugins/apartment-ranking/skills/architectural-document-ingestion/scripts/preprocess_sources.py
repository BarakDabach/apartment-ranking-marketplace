#!/usr/bin/env python3
"""Create a lightweight architectural-document cache from PDFs and images.

Deterministic only: hashing, native text extraction, low-resolution preview rendering,
page Markdown scaffolds, and a manifest. It intentionally does not infer architectural
semantics such as facades, directions, rooms, or parking zones.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import fitz  # PyMuPDF
from PIL import Image

SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(name: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-._") or "source"
    return stem[:80]


def iter_sources(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    for p in sorted(input_path.rglob("*")):
        if p.is_file() and (p.suffix.lower() == ".pdf" or p.suffix.lower() in SUPPORTED_IMAGES):
            yield p


def save_webp(img: Image.Image, path: Path, max_width: int, quality: int) -> None:
    img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, max(1, round(img.height * ratio))), Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "WEBP", quality=quality, method=6)


def md_text(source_id: str, filename: str, sha: str, page_num: int, preview_rel: str, native_text: str) -> str:
    text = native_text.strip()
    return f'''---\nsource_id: "{source_id}"\nsource_file: "{filename}"\nsource_sha256: "{sha}"\npage: {page_num}\npage_type: null\nplot: null\nbuilding: null\nfloor: null\napartment_refs: []\nnorth_or_compass_visible: null\nrelevant_for: []\nreview_status: unreviewed\npreview: "{preview_rel}"\n---\n\n# Page {page_num}\n\n## Extracted native text\n\n{text if text else "_No useful native text extracted._"}\n\n## Architectural observations\n\n<!-- Agent: add only verified observations. Do not encode full geometry here. -->\n\n## Evidence crops\n\n<!-- Add relative crop paths when detail crops are created from the original source. -->\n'''


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def process_pdf(path: Path, cache: Path, source_id: str, sha: str, dpi: int, max_width: int, quality: int):
    doc = fitz.open(path)
    pages = []
    for idx in range(doc.page_count):
        page_num = idx + 1
        page = doc.load_page(idx)
        native_text = page.get_text("text") or ""
        pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0), alpha=False)
        mode = "RGB" if pix.n < 4 else "RGBA"
        img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
        preview = cache / "previews" / source_id / f"p{page_num:04d}.webp"
        save_webp(img, preview, max_width, quality)
        md = cache / "pages" / source_id / f"p{page_num:04d}.md"
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(md_text(source_id, path.name, sha, page_num, relpath(preview, cache), native_text), encoding="utf-8")
        rect = page.rect
        pages.append({
            "page_number": page_num,
            "width_points": round(float(rect.width), 3),
            "height_points": round(float(rect.height), 3),
            "native_text_chars": len(native_text),
            "markdown_path": relpath(md, cache),
            "preview_path": relpath(preview, cache),
            "page_type": None,
            "plot": None,
            "building": None,
            "floor": None,
            "apartment_refs": [],
            "north_or_compass_visible": None,
            "relevant_for": [],
            "review_status": "unreviewed",
        })
    doc.close()
    return pages


def process_image(path: Path, cache: Path, source_id: str, sha: str, max_width: int, quality: int):
    with Image.open(path) as im:
        img = im.convert("RGB")
        original_w, original_h = img.size
        preview = cache / "previews" / source_id / "p0001.webp"
        save_webp(img, preview, max_width, quality)
    md = cache / "pages" / source_id / "p0001.md"
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(md_text(source_id, path.name, sha, 1, relpath(preview, cache), ""), encoding="utf-8")
    return [{
        "page_number": 1,
        "width_points": None,
        "height_points": None,
        "native_text_chars": 0,
        "markdown_path": relpath(md, cache),
        "preview_path": relpath(preview, cache),
        "page_type": None,
        "plot": None,
        "building": None,
        "floor": None,
        "apartment_refs": [],
        "north_or_compass_visible": None,
        "relevant_for": [],
        "review_status": "unreviewed",
    }]


def load_existing(cache: Path) -> dict:
    p = cache / "manifest.json"
    if not p.exists():
        return {"schema_version": 1, "generated_at_utc": "", "sources": []}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "generated_at_utc": "", "sources": []}


def write_index(cache: Path, manifest: dict) -> None:
    lines = ["# Architectural Source Index", "", "Generated cache for lightweight routing. Original sources remain authoritative.", ""]
    for src in manifest["sources"]:
        lines += [f"## {src['filename']}", "", f"- Source id: `{src['source_id']}`", f"- SHA-256: `{src['sha256']}`", f"- Pages: {src['page_count']}", ""]
        lines.append("| Page | Type | Review | Native text chars | Markdown | Preview |")
        lines.append("|---:|---|---|---:|---|---|")
        for p in src["pages"]:
            lines.append(f"| {p['page_number']} | {p.get('page_type') or ''} | {p.get('review_status','')} | {p.get('native_text_chars',0)} | `{p['markdown_path']}` | `{p['preview_path']}` |")
        lines.append("")
    (cache / "index.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Source file or directory")
    ap.add_argument("--output", required=True, help="Cache directory")
    ap.add_argument("--preview-dpi", type=int, default=110)
    ap.add_argument("--max-preview-width", type=int, default=1800)
    ap.add_argument("--webp-quality", type=int, default=68)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    cache = Path(args.output).expanduser().resolve()
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "derived").mkdir(exist_ok=True)
    facts = cache / "derived" / "facts.json"
    if not facts.exists():
        facts.write_text(json.dumps({"schema_version": 1, "facts": []}, indent=2), encoding="utf-8")

    existing = load_existing(cache)
    existing_by_sha = {s.get("sha256"): s for s in existing.get("sources", []) if s.get("sha256")}
    new_sources = []

    sources = list(iter_sources(input_path))
    if not sources:
        raise SystemExit("No supported PDF/image sources found.")

    for path in sources:
        sha = sha256_file(path)
        if not args.force and sha in existing_by_sha:
            src = existing_by_sha[sha]
            all_exist = all((cache / p["markdown_path"]).exists() and (cache / p["preview_path"]).exists() for p in src.get("pages", []))
            if all_exist:
                new_sources.append(src)
                print(f"REUSE {path.name} -> {src['source_id']}")
                continue

        source_id = f"{slugify(path.stem)}-{sha[:8]}"
        media_type = mimetypes.guess_type(path.name)[0] or ("application/pdf" if path.suffix.lower() == ".pdf" else "image/unknown")
        if path.suffix.lower() == ".pdf":
            pages = process_pdf(path, cache, source_id, sha, args.preview_dpi, args.max_preview_width, args.webp_quality)
        elif path.suffix.lower() in SUPPORTED_IMAGES:
            pages = process_image(path, cache, source_id, sha, args.max_preview_width, args.webp_quality)
        else:
            continue
        new_sources.append({
            "source_id": source_id,
            "original_path": str(path),
            "filename": path.name,
            "sha256": sha,
            "media_type": media_type,
            "size_bytes": path.stat().st_size,
            "page_count": len(pages),
            "pages": pages,
        })
        print(f"BUILD {path.name} -> {source_id} ({len(pages)} page(s))")

    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": new_sources,
    }
    (cache / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_index(cache, manifest)
    print(f"WROTE {cache / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
