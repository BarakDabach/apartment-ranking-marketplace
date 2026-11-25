# Changelog

## 1.2.0

Works with any skills-compatible agent, not only Codex / ChatGPT.

- Added Claude Code manifests: `.claude-plugin/marketplace.json` (also read by GitHub Copilot in VS Code and Copilot CLI) and `plugins/apartment-ranking/.claude-plugin/plugin.json`.
- Added `scripts/install-skills.ps1` / `.sh` to copy both skills into Claude, Copilot, Codex, or any custom skills folder, backing up existing copies outside the skills folder.
- `apartment-ranking` SKILL.md: host-neutral sibling-skill invocation (`$...` / `/...` / read `../architectural-document-ingestion/SKILL.md`) and a rule for bank edits made in a managed plugin install.
- README: install and usage instructions per agent.
- Verifier: checks the Claude manifests, a single shared version, and Agent Skills frontmatter (name = directory, description ≤ 1024 characters).

## 1.1.0

Merged the lessons of project 2181 (שמורת אלמוגים – חיפה, 15 buildings, 3 plots) into 1.0.5.

- Criteria bank: Quiet v3 (off-plot check against the neighborhood map, mandatory external noise-source checklist, ramp/transformer/sealed-void/meter-cabinet cases), Location on Floor v2 (lobby, shaft-type and amenity-wall rules), Facades boundary rules, Parking Proximity v2 (measurement rule, meters + building-zone note, mixed-level ownership, appendix duplicates, 6↔9 rotated labels), new Storage Proximity v1.
- Canonical `excel_explanation` texts are the detailed project-2181 wording; score explanations stay short.
- New Phase -1 Step C: ask whether a טופס ג'4 parking/storage assignment appendix exists before activating parking/storage proximity.
- Source-link columns are optional per project (asked at setup; default none).
- Parking / storage proximity workflow for vector common-area plans and bundled `scripts/plan_walk.py` (wall-aware walking distance).
- Neighborhood overview map added as a source for external exposures.
- Ingestion: guided DWF ingestion reference; storage/core/scale cache fields.

## 1.0.5

- Made criterion `display_name` and `excel_explanation` strict canonical cross-project metadata.
- Existing criteria are copied verbatim from the criteria bank into every new project; agents may not paraphrase or project-adapt them.
- New criteria become canonical immediately when persisted to the bank.
- Explicit name/description changes now require updating/versioning the bank definition before use.
- Added workbook validation for criterion metadata consistency.

## 1.0.4

- Added `agents/openai.yaml` metadata for both packaged skills.
- Enabled implicit invocation for `apartment-ranking` and explicit-only invocation for `architectural-document-ingestion`.
- Converted distribution to a standard repository marketplace layout for cross-machine use.
- Added Git/CLI installation instructions and local registration scripts.
- Added explicit Python dependency metadata for the optional deterministic ingestion preprocessor.
- Updated plugin install-facing metadata and starter prompts.

## 1.0.3

- Made Excel output incremental: each completed building is written, validated, and saved before the next building begins.
- Removed the five source-link columns from the canonical workbook/template and skill contract.

## 1.0.2

- Required exact short negative causes for low scores in `מיקום בקומה` and `שקט/רעש`.

## 1.0.1

- Shortened criterion and score explanations.

## 1.0.0

- First Apartment Ranking plugin version with apartment ranking and architectural document ingestion skills.
