# Changelog

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
