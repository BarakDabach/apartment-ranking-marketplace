---
name: architectural-document-ingestion
description: Cache-first ingestion workflow for architectural PDFs and plan images. Converts heavy source files into a lightweight, traceable project cache containing source hashes, page-level Markdown, low-resolution WebP previews, extracted native text, page classifications, targeted detail crops, and normalized derived facts with evidence pointers. Use before repeated analysis of floor plans, site plans, parking plans, sections, elevations, or apartment drawings. Markdown/JSON are navigation and cache layers; original drawings remain authoritative for geometry.
---

# Architectural Document Ingestion

Build a reusable lightweight evidence cache from architectural PDFs and images so downstream analysis does not repeatedly consume entire heavy drawings.

This skill is **not** an autonomous CAD interpreter. Deterministic preprocessing creates previews, native-text extracts, hashes, and manifests; the agent then performs visual architectural interpretation and records only verified facts with source evidence.

## Goals

1. Avoid reopening whole PDFs for every criterion or apartment.
2. Preserve traceability from every derived fact back to the original source/page/crop.
3. Keep original PDFs/images as the authority for geometry.
4. Allow new criteria to reuse previously extracted facts without reprocessing unchanged source files.
5. Escalate image resolution only when needed.

## Portable runtime requirements

The skill instructions themselves are portable. The optional deterministic preprocessing script `scripts/preprocess_sources.py` requires Python 3 plus the packages listed in `requirements.txt` (`PyMuPDF` and `Pillow`). If those packages are unavailable, prefer the platform PDF/image capability rather than silently skipping ingestion. Do not assume a machine-specific Python path.

## Required companion capabilities

When available, use the platform's PDF capability for authoritative PDF inspection, high-resolution rendering, cropping, and difficult extraction. For spreadsheet output, delegate workbook operations to the spreadsheet capability rather than implementing workbook logic here.

OCR is a last resort. Prefer native PDF text extraction and visual inspection of the drawing. Never let OCR override visible geometry, compass orientation, dimensions, or linework.

## Output contract

Default cache root:

```text
project-cache/
├── manifest.json
├── index.md
├── pages/
│   └── <source-id>/
│       ├── p0001.md
│       └── ...
├── previews/
│   └── <source-id>/
│       ├── p0001.webp
│       └── ...
├── crops/
│   └── <source-id>/
│       └── ...
└── derived/
    └── facts.json
```

The cache is disposable and reproducible. The original source files are not replaced.

## Stage 1 - Deterministic preprocessing

Run `scripts/preprocess_sources.py` against the project's PDF/image sources.

The script:

- computes SHA-256 for every source;
- assigns a stable source id based on filename + hash prefix;
- records media type and page count;
- extracts **native PDF text** page by page when present;
- renders lightweight WebP page previews;
- creates one Markdown file per page;
- creates `manifest.json` and `index.md`;
- reuses unchanged cached sources instead of regenerating them.

Typical command:

```bash
python scripts/preprocess_sources.py \
  --input /path/to/project-sources \
  --output /path/to/project-cache
```

Default preview settings are intentionally lightweight. They are for page discovery and classification, not final geometric proof.

## Stage 2 - Page classification

Use the lightweight preview + page Markdown to classify each relevant page.

Recommended page types:

- `typical-floor-plan`
- `apartment-plan`
- `site-plan`
- `parking-plan`
- `storage-plan`
- `section`
- `elevation`
- `schedule-or-table`
- `specification`
- `cover-or-index`
- `other`

For each reviewed page, update its Markdown metadata/notes and the manifest with:

- page type;
- plot/building/floor when identifiable;
- apartment types/numbers when identifiable;
- whether compass/north is visible;
- criteria/evidence categories the page can support;
- review status.

Do not force classification when the page is ambiguous.

## Stage 3 - Resolution escalation

Use three levels:

### Level 1 - Index preview

Use the cached WebP preview for:

- title block recognition;
- page subject classification;
- finding candidate buildings/apartments;
- locating compass, legends, sections, parking zones.

Do **not** make fine geometric claims solely from a low-resolution preview.

### Level 2 - Relevant page

Open/render only the specific original PDF page needed for a criterion or fact.

Use it for:

- general apartment boundaries;
- core relationship;
- orientation;
- site context;
- parking-zone interpretation.

### Level 3 - Detail crop

Create a high-resolution crop from the original drawing when linework, labels, dimensions, openings, or wall relationships are too small on the page view.

Store reusable crops under `crops/<source-id>/` and reference them from derived facts.

Never upscale a low-resolution cached preview and treat it as new evidence. Detail crops must originate from the original PDF/image.

## Stage 4 - Normalize verified facts

Write reusable project facts to `derived/facts.json` using the contract in `references/cache-contract.md` and `schemas/derived-facts.schema.json`.

Prefer small atomic facts over criterion-specific conclusions.

Good facts:

- apartment A3 has two verified exterior facades;
- apartment A3 primary exposures are south and west;
- living room wall touches elevator shaft;
- building 3 typical floor has four apartments;
- parking 214 belongs to apartment 37;
- parking 214 is approximately 42 m walking route from building 3 core;
- west facade faces a major road.

Avoid storing only conclusions such as `quiet_score = 6` when the underlying observations can be stored instead. Criteria can then be changed without re-reading the drawing.

## Evidence contract

Every derived fact must contain at least one evidence pointer:

- `source_id`;
- page number for PDFs;
- optional crop path;
- concise observation note;
- confidence (`high`, `medium`, `low`).

If a fact cannot be tied to evidence, do not promote it into the derived fact store.

## Cache-first downstream use

Before reopening source documents for a question or criterion:

1. check `derived/facts.json` for all required observations;
2. check page Markdown/manifest for already-reviewed evidence;
3. reuse cached high-resolution crops when they are sufficient;
4. reopen the original page only for missing, ambiguous, or newly required facts.

This is especially important when a new criterion is added after apartments were already analyzed.

## Invalidation

Source hash is the invalidation key.

- If SHA-256 is unchanged, reuse the source's preprocessing cache.
- If SHA-256 changes, invalidate that source's page previews/text and mark facts that depend on it as needing re-verification.
- Do not invalidate unrelated sources.

Run `scripts/validate_cache.py` before relying on an existing cache.

## Markdown rules

Page Markdown is a navigation layer. Keep it concise.

Each page Markdown should contain:

- source identity/hash;
- page number;
- preview path;
- extracted native text (when useful, truncated only if enormous);
- classification metadata;
- architectural observations entered by the agent;
- evidence/crop links.

Do not attempt to encode the full geometry of a plan in Markdown.

## Quality rules

1. Original drawing geometry outranks OCR/text.
2. Compass + actual exterior/opening walls outrank marketing direction text.
3. Low-res previews are discovery aids, not fine-detail proof.
4. Never infer a parking zone from parking number alone.
5. Never count corridor/core/shared walls as exterior facades.
6. Preserve uncertainty explicitly.
7. Store atomic facts so future criteria can reuse them.
8. Never delete original source files after cache generation.

## Completion checklist

The ingestion pass is complete when:

- every source has a SHA-256 entry;
- page/image previews exist;
- page Markdown exists;
- relevant pages are classified enough to route analysis;
- any facts used downstream have evidence pointers;
- the cache validates successfully;
- unresolved/ambiguous pages remain marked as such rather than guessed.
