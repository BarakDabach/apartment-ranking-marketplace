# Apartment Ranking Plugin Marketplace

Portable repository marketplace for the **Apartment Ranking** plugin. The skills follow the open [Agent Skills](https://agentskills.io/) standard and the package ships manifests for Claude Code, GitHub Copilot (VS Code / CLI), OpenAI Codex, and the [Agent Plugins](https://agent-plugins.org/) format, so it works with any skills-compatible agent.

The plugin contains two skills:

- `apartment-ranking` — project orchestration, criteria bank, scoring, and incremental Excel output.
- `architectural-document-ingestion` — cache-first preprocessing of architectural PDFs/images into Markdown, JSON, WebP previews/crops, and derived evidence.

## Repository layout

```text
.
├── .claude-plugin/marketplace.json      # Claude Code + GitHub Copilot marketplace
├── .agents/plugins/marketplace.json     # Codex marketplace
├── scripts/install-skills.ps1|.sh       # plain copy into any agent's skills folder
└── plugins/apartment-ranking/
    ├── plugin.json                      # Agent Plugins 1.0 (Copilot, other clients)
    ├── .claude-plugin/plugin.json       # Claude Code
    ├── .codex-plugin/plugin.json        # Codex
    └── skills/
        ├── apartment-ranking/
        │   ├── SKILL.md
        │   ├── agents/openai.yaml
        │   ├── references/
        │   ├── scripts/
        │   └── assets/
        └── architectural-document-ingestion/
            ├── SKILL.md
            ├── agents/openai.yaml
            ├── requirements.txt
            ├── scripts/
            ├── schemas/
            └── references/
```

## Install

The two skills must always be installed together. Pick the route for your agent.

### Claude Code

```bash
claude plugin marketplace add BarakDabach/apartment-ranking-marketplace
claude plugin install apartment-ranking@apartment-ranking-tools
```

Inside a session the same works with `/plugin marketplace add ...` and `/plugin install ...`. Update later with `claude plugin marketplace update apartment-ranking-tools`.

### GitHub Copilot in VS Code

Run **Chat: Install Plugin from Source** and enter `https://github.com/BarakDabach/apartment-ranking-marketplace`, or add `BarakDabach/apartment-ranking-marketplace` under **Configure Marketplaces** (setting `chat.plugins.marketplaces`) and install **apartment-ranking**. Requires `chat.plugins.enabled`.

### GitHub Copilot CLI

```bash
copilot plugin marketplace add BarakDabach/apartment-ranking-marketplace
copilot plugin install apartment-ranking@apartment-ranking-tools
```

### OpenAI Codex / ChatGPT desktop

```bash
codex plugin marketplace add BarakDabach/apartment-ranking-marketplace --ref main
```

Then restart, open the Plugin Directory, select **Apartment Ranking Tools**, and install **Apartment Ranking**. Update with `codex plugin marketplace upgrade apartment-ranking-tools`. From a local clone you can also run `./scripts/register-local.ps1` or `./scripts/register-local.sh`.

### Any other skills-compatible agent (no plugin system)

Clone the repository and copy both skills into the agent's skills folder:

```powershell
./scripts/install-skills.ps1 -Agent claude        # ~/.claude/skills
./scripts/install-skills.ps1 -Agent copilot       # ~/.copilot/skills
./scripts/install-skills.ps1 -Agent codex         # ~/.agents/skills
./scripts/install-skills.ps1 -Path <skills-dir>   # any other agent or a project folder (.github/skills, .claude/skills, ...)
```

```bash
./scripts/install-skills.sh claude copilot codex
./scripts/install-skills.sh --path <skills-dir>
```

Existing copies are moved to a `skills-backup/<timestamp>/` folder next to the skills folder first, so local criteria-bank additions are not lost. For an agent with no skill support at all, point it at `plugins/apartment-ranking/skills/apartment-ranking/SKILL.md` and ask it to follow that file.

### Criteria-bank changes

The skill writes new criteria into `references/criteria-bank.md` of the copy it runs from. Plugin installs live in a managed cache that is replaced on update, so commit bank changes back to this repository and bump the version.

## Usage

Ask for an apartment ranking project and the agent loads the skill automatically, or invoke it explicitly:

| Agent | Primary skill | Ingestion skill |
| --- | --- | --- |
| Claude Code / GitHub Copilot | `/apartment-ranking` (plugin install: `/apartment-ranking:apartment-ranking`) | `/architectural-document-ingestion` |
| Codex | `$apartment-ranking` | `$architectural-document-ingestion` |

The primary skill delegates architectural PDF/image preprocessing to the sibling skill when needed.

## Local preprocessing dependencies

The deterministic ingestion helper requires Python 3 and:

```bash
python -m pip install -r plugins/apartment-ranking/skills/architectural-document-ingestion/requirements.txt
```

If those packages are not available, the skill should use the host's PDF/image capability instead of assuming a machine-specific environment.

The parking/storage walking-distance helper `plugins/apartment-ranking/skills/apartment-ranking/scripts/plan_walk.py` uses the same packages (PyMuPDF + Pillow).

