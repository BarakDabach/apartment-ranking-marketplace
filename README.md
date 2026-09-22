# Apartment Ranking Plugin Marketplace

Portable repository marketplace for the **Apartment Ranking** plugin.

The plugin contains two skills:

- `apartment-ranking` — project orchestration, criteria bank, scoring, and incremental Excel output.
- `architectural-document-ingestion` — cache-first preprocessing of architectural PDFs/images into Markdown, JSON, WebP previews/crops, and derived evidence.

## Repository layout

```text
.
├── .agents/plugins/marketplace.json
└── plugins/apartment-ranking/
    ├── plugin.json
    ├── .codex-plugin/plugin.json
    └── skills/
        ├── apartment-ranking/
        │   ├── SKILL.md
        │   ├── agents/openai.yaml
        │   ├── references/
        │   └── assets/
        └── architectural-document-ingestion/
            ├── SKILL.md
            ├── agents/openai.yaml
            ├── requirements.txt
            ├── scripts/
            ├── schemas/
            └── references/
```

## Install from an extracted folder

From a terminal with the Codex CLI available:

```bash
codex plugin marketplace add /absolute/path/to/this/repository
```

On Windows PowerShell you can also run:

```powershell
./scripts/register-local.ps1
```

On macOS/Linux:

```bash
./scripts/register-local.sh
```

Then restart ChatGPT desktop / Codex, open the Plugin Directory, select **Apartment Ranking Tools**, and install **Apartment Ranking**.

## Use on any machine through Git

This repository is ready to push to a Git host. Once it is in GitHub, every machine can register the same marketplace without copying the plugin files manually:

```bash
codex plugin marketplace add OWNER/REPOSITORY --ref main
```

A full HTTPS/SSH Git URL is also supported. After registration, restart ChatGPT desktop / Codex and install **Apartment Ranking** from **Apartment Ranking Tools**.

To pull marketplace/plugin updates later:

```bash
codex plugin marketplace upgrade apartment-ranking-tools
```

## Usage

Primary skill:

```text
$apartment-ranking
```

The primary skill delegates architectural PDF/image preprocessing to the sibling skill when needed. The ingestion skill can also be called explicitly:

```text
$architectural-document-ingestion
```

## Local preprocessing dependencies

The deterministic ingestion helper requires Python 3 and:

```bash
python -m pip install -r plugins/apartment-ranking/skills/architectural-document-ingestion/requirements.txt
```

If those packages are not available, the skill should use the host's PDF/image capability instead of assuming a machine-specific environment.

