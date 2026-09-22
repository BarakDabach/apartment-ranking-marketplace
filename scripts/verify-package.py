#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "apartment-ranking"
errors: list[str] = []

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"Invalid JSON {path.relative_to(ROOT)}: {e}")
        return None

market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
manifest = load_json(PLUGIN / "plugin.json")
compat = load_json(PLUGIN / ".codex-plugin" / "plugin.json")

if market:
    if market.get("name") != "apartment-ranking-tools":
        errors.append("Marketplace name must be apartment-ranking-tools")
    plugins = market.get("plugins") or []
    if len(plugins) != 1 or plugins[0].get("name") != "apartment-ranking":
        errors.append("Marketplace must expose exactly the apartment-ranking plugin")
    else:
        source = plugins[0].get("source", {})
        if source.get("path") != "./plugins/apartment-ranking":
            errors.append("Marketplace source path is not portable")
        policy = plugins[0].get("policy", {})
        if not policy.get("installation") or not policy.get("authentication"):
            errors.append("Marketplace policy must include installation and authentication")

if manifest:
    if manifest.get("name") != "apartment-ranking":
        errors.append("Portable manifest name mismatch")
    if manifest.get("version") != "1.0.5":
        errors.append("Portable manifest version mismatch")
    if manifest.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        errors.append("Portable manifest schema mismatch")
    ui = ((manifest.get("extensions") or {}).get("com.openai") or {}).get("interface") or {}
    if not ui.get("displayName") or not ui.get("shortDescription") or not ui.get("longDescription"):
        errors.append("Portable manifest is missing OpenAI interface metadata")
    prompts = ui.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts:
        errors.append("Portable manifest defaultPrompt must be a non-empty list")

if compat:
    if compat.get("skills") != "./skills/":
        errors.append("Compatibility manifest must point skills to ./skills/")
    if compat.get("version") != "1.0.5":
        errors.append("Compatibility manifest version mismatch")

# Guard the cross-project canonical criterion identity contract.
ranking_skill = (PLUGIN / "skills" / "apartment-ranking" / "SKILL.md").read_text(encoding="utf-8")
criteria_bank = (PLUGIN / "skills" / "apartment-ranking" / "references" / "criteria-bank.md").read_text(encoding="utf-8")
if "Canonical criterion identity — strict cross-project rule" not in ranking_skill:
    errors.append("Ranking skill is missing the canonical cross-project criterion identity rule")
if "canonical cross-project metadata" not in criteria_bank:
    errors.append("Criteria bank is missing the canonical cross-project metadata policy")

for skill in ("apartment-ranking", "architectural-document-ingestion"):
    root = PLUGIN / "skills" / skill
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"Missing {skill}/SKILL.md")
    else:
        head = skill_md.read_text(encoding="utf-8")[:2500]
        if f"name: {skill}" not in head:
            errors.append(f"{skill}/SKILL.md frontmatter name mismatch")
    agent = root / "agents" / "openai.yaml"
    if not agent.is_file():
        errors.append(f"Missing {skill}/agents/openai.yaml")
        continue
    text = agent.read_text(encoding="utf-8")
    for required in ("interface:", "display_name:", "short_description:", "default_prompt:", "policy:", "allow_implicit_invocation:"):
        if required not in text:
            errors.append(f"{skill}/agents/openai.yaml missing {required}")

# Verify workbook without requiring spreadsheet libraries: XLSX is a ZIP of XML files.
def xlsx_shared_strings(z: zipfile.ZipFile) -> list[str]:
    try:
        raw = z.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ET.fromstring(raw)
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    out=[]
    for si in root.findall("m:si", ns):
        parts=[t.text or "" for t in si.findall(".//m:t", ns)]
        out.append("".join(parts))
    return out

def workbook_headers(path: Path, target_sheet_name: str) -> tuple[list[str], list[str]]:
    ns_main="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ns_rel_doc="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ns_rel_pkg="http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(path) as z:
        wb=ET.fromstring(z.read("xl/workbook.xml"))
        names=[]; rid=None
        for sh in wb.findall(f"{{{ns_main}}}sheets/{{{ns_main}}}sheet"):
            name=sh.attrib.get("name",""); names.append(name)
            if name==target_sheet_name:
                rid=sh.attrib.get(f"{{{ns_rel_doc}}}id")
        if rid is None:
            return names, []
        rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target=None
        for rel in rels.findall(f"{{{ns_rel_pkg}}}Relationship"):
            if rel.attrib.get("Id")==rid:
                target=rel.attrib.get("Target")
                break
        if not target:
            return names, []
        if target.startswith("/"):
            sheet_path=target.lstrip("/")
        else:
            sheet_path="xl/"+target.lstrip("./")
        xml=ET.fromstring(z.read(sheet_path))
        shared=xlsx_shared_strings(z)
        row=xml.find(f".//{{{ns_main}}}sheetData/{{{ns_main}}}row[@r='1']")
        if row is None:
            return names, []
        vals=[]
        for c in row.findall(f"{{{ns_main}}}c"):
            typ=c.attrib.get("t")
            if typ=="inlineStr":
                t=c.find(f".//{{{ns_main}}}t")
                vals.append(t.text if t is not None and t.text else "")
            else:
                v=c.find(f"{{{ns_main}}}v")
                raw=v.text if v is not None and v.text else ""
                if typ=="s" and raw.isdigit() and int(raw)<len(shared):
                    vals.append(shared[int(raw)])
                else:
                    vals.append(raw)
        return names, vals

try:
    xlsx = PLUGIN / "skills" / "apartment-ranking" / "assets" / "project-template-reference.xlsx"
    names, headers = workbook_headers(xlsx, "Apartments")
    if set(names) != {"Lottery", "Apartments"}:
        errors.append(f"Unexpected workbook sheets: {names}")
    forbidden = {"קישור", "PDF דירה", "PDF קומות", "PDF פיתוח", "PDF צבעוני"}
    present = forbidden.intersection(set(headers))
    if present:
        errors.append(f"Removed link columns returned: {sorted(present)}")
except Exception as e:
    errors.append(f"Workbook verification failed: {e}")

if errors:
    print("PACKAGE INVALID")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print("PACKAGE OK")
print(f"Repository root: {ROOT}")
print("Plugin: apartment-ranking 1.0.5")
print("Skills: apartment-ranking, architectural-document-ingestion")
