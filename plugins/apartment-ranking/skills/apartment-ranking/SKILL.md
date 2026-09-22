---
name: apartment-ranking
description: End-to-end, cache-first pipeline for creating and maintaining a project-level apartment analysis dataset from architectural source documents (floor plans, site plans, parking layouts, cross-sections, spec booklets). For every new project, load the persistent criteria bank, select active criteria, optionally define/persist new reusable criteria, generate the standard `Lottery` + `Apartments` Excel workbook, preprocess heavy PDF/image sources through the sibling `architectural-document-ingestion` skill included in the same plugin, and analyze/write apartments building by building. Supports adding or versioning criteria later and retroactively rescoring already-analyzed buildings while reusing cached atomic facts and evidence whenever possible.
---

# Apartment Ranking / Project Analysis Pipeline

Turn architectural project documents into a defensible, reusable apartment dataset.

The skill produces **project-level apartment analysis**. It does not decide the user's personal apartment preference.

The project's workbook has exactly two sheets:

1. `Lottery` — project metadata.
2. `Apartments` — apartment facts, selected project-level criteria, and score explanations.

Personalized ranking belongs downstream in the application. In particular, **floor preference is not a project-level criterion**. The raw floor number is stored in `Apartments`, and the application recalculates the floor preference score per user.

## Persistent criteria bank

The skill has a persistent reusable criterion registry stored in:

`references/criteria-bank.md`

This bank is part of the skill itself, not part of a single project.

Every approved new project-level criterion must be added to this bank with its complete analysis definition. From that point forward it is offered automatically when starting every future project.

A criterion being present in the bank does **not** mean it is automatically active in every project. The bank defines what the skill knows how to analyze; the user chooses which bank criteria are active for each project.

When packaging or exporting the skill, always include the current `references/criteria-bank.md`. Otherwise the skill loses criteria learned in previous projects.


## Canonical criterion identity — strict cross-project rule

For every criterion that already exists in `references/criteria-bank.md`, the bank is the canonical source for both:

- `display_name` → the exact value written to Excel under `שם הקריטריון`;
- `excel_explanation` → the exact value written to Excel under `הסבר הקריטריון`.

For a **new project**, when the user activates an existing bank criterion, copy these two values **verbatim from the bank**. Do not paraphrase, translate, shorten, expand, normalize punctuation, or adapt wording to the current project. The same criterion key/version must therefore use the same criterion name and criterion description across all new projects.

When a **new criterion is first created**, confirm its canonical `display_name` and `excel_explanation`, persist them in the bank, and then use those exact values in the current project and all future projects.

Do not create project-local aliases or alternate criterion descriptions in Excel by default. If the user explicitly asks to change the criterion name or generic description, treat that as a change to the reusable bank definition: update/version the bank entry first, then use the new canonical values. Historical projects are not silently rewritten unless the user explicitly requests a migration/refactor.

## Companion skill integration and capability routing

This plugin also installs the sibling skill `architectural-document-ingestion`.

Whenever project evidence arrives as architectural PDFs or plan images, load/invoke `architectural-document-ingestion` before repeated apartment analysis. If explicit skill invocation is supported, use `$architectural-document-ingestion`; otherwise resolve the sibling skill from the same plugin. Do not maintain a nested duplicate copy inside this skill.

Use it whenever project evidence arrives as PDFs or plan images. Its job is to create a lightweight, reusable evidence cache containing source hashes, page-level Markdown, low-resolution WebP previews, page classifications, targeted detail crops, and normalized atomic facts with evidence pointers.

The apartment-ranking skill owns **domain logic and scoring**. The ingestion companion owns **source preprocessing, cache structure, evidence routing, and invalidation**.

When the execution environment provides specialized capabilities:

- use the **PDF capability** for authoritative PDF inspection, high-resolution page rendering/cropping, and difficult extraction;
- use the **spreadsheet capability** for all `.xlsx` creation/modification/validation;
- use OCR only when native text extraction and visual inspection are insufficient, and never let OCR override visible architectural geometry.

The original drawings remain authoritative. Markdown/JSON/WebP outputs are cache and navigation layers, not replacements for the source documents.

---

# Core operating model

The pipeline always follows this order:

1. **Load the persistent criteria bank.**
2. **Show the user every criterion currently supported by the skill.**
3. **Let the user select the active criteria for this project.**
4. **Ask whether the user wants to define additional criteria.**
5. **For every approved new criterion, persist its full definition into the skill's criteria bank.**
6. **Generate the standard Excel workbook for the project.**
7. **Collect project source documents and run the sibling `architectural-document-ingestion` workflow.**
8. **Classify only the pages relevant to the active criteria and build/reuse the project evidence cache.**
9. **Analyze one building completely, using cached atomic facts first and reopening original drawings only when evidence is missing/ambiguous.**
10. **Present that building's analysis/scores for approval.**
11. **Write that building to `Apartments` and save a checkpoint.**
12. Repeat for the next building.

If a criterion is added or changed after some buildings have already been analyzed, the pipeline pauses forward analysis, updates the criteria bank first, retrofits the criterion across all completed buildings, saves the workbook building by building, and only then continues.

---

# Non-negotiable rules

1. **Never auto-exclude apartment types.**
   Do not skip 6-room units, 7-room units, penthouses, duplexes, ground floors, or any other type unless the user explicitly says to.

2. **Criteria are selected before analysis starts.**
   For a new project, first load `references/criteria-bank.md`, show every supported criterion, and do not analyze or score apartments until the user has confirmed the active criterion set.

3. **Floor is raw data, not a project criterion.**
   Keep `קומה` in the fixed apartment fields. Do not create a `קומה` / floor criterion block and do not compute a project-level floor score.

4. **The criterion schema is dynamic.**
   Never hard-code the number of criteria or their Excel letters. Every active criterion occupies one repeating 4-column block.

5. **Every approved new criterion extends the skill.**
   A newly defined criterion must be persisted into `references/criteria-bank.md` before it is used. It is then available for all future projects. Do not keep a fully defined criterion only inside the current project's conversation.

6. **Use the workbook structure defined in this skill exactly.**
   Do not create extra sheets, weight columns, final-score columns, or criterion-specific raw-data columns unless the user explicitly changes the contract.

7. **Present a completed building for approval before writing it**, unless the user explicitly waived this approval step.

8. **Verify every directional claim against the drawing.**
   Do not trust textual direction descriptions when they conflict with the compass and actual exterior/opening walls.

9. **A wall is only an exterior facade when it actually faces outside air and has relevant exterior openings.**
   Neighbor/core/corridor walls are not facades.

10. **Work building by building and save after every approved building.**

    The Excel workbook is an **incremental project artifact**, not an end-of-project export. After a building is fully analyzed and approved (or immediately after analysis if the approval step was explicitly waived), write all of that building's apartment rows to the project workbook, validate the write, and save the workbook **before starting analysis of the next building**. Never keep a completed building only in conversation state, Markdown, JSON, or cache. If work stops after N completed buildings, the saved workbook must already contain those N buildings.

11. **State uncertainty explicitly.**
    Never silently infer an unreadable parking number, ambiguous elevation, unclear wall condition, or missing source fact.

12. **Score cells contain numbers only.**
    No `N/A`, `?`, explanations, symbols, or text in `ציון`.

13. **A blank score means unresolved/not yet analyzed.**
    Do not convert missing analysis into `0`.

14. **Existing project convention takes precedence when continuing an existing workbook.**
    Precedence:
    1. explicit current user instruction;
    2. established scoring convention in that project/workbook;
    3. built-in fallback scoring rules from this skill.

15. **Project facts and user preferences stay separate.**
    User-specific weights, budget filters, floor preferences, and other personal ranking settings do not belong in this workbook.

16. **Use cache-first evidence retrieval.**
    Before reopening a heavy PDF/image, check the bundled ingestion cache for the required atomic observations, reviewed page Markdown, and reusable high-resolution crops. Reopen the original source only when the needed evidence is missing, stale, ambiguous, or too low-resolution.

17. **Never promote cache summaries above the source drawing.**
    Markdown, extracted text, JSON facts, and low-resolution WebP previews are derived helpers. Fine geometric claims must still be traceable to the original page/image or a crop rendered directly from it.

18. **Do not reprocess unchanged source files.**
    Use SHA-256 source hashes from the ingestion companion. If a source hash is unchanged, reuse its preprocessing cache. If it changes, invalidate only facts that depend on that source.


19. **Criterion identity is canonical across projects.**
    For every existing bank criterion, write `display_name` and `excel_explanation` exactly as stored in `references/criteria-bank.md`. Do not rewrite them per project or per apartment. If the user explicitly requests a name/description change, update/version the bank definition first; do not silently create a project-only variant.

---

# Phase -1 — Criteria setup

This phase happens **before any apartment analysis on every new project**.

## Step A — Load and show the criteria bank

Read `references/criteria-bank.md` before asking the user to choose criteria.

Show **every active criterion in the bank**. Do not maintain a second hard-coded list in the workflow.

Do not offer Floor/Floor Preference as a project criterion.

For each bank criterion shown to the user, summarize:

- display name;
- purpose;
- what it measures;
- required/typical evidence sources;
- applicability;
- scoring range;
- whether it can be non-applicable.

Then ask the user which criteria to activate for this project.

When an existing bank criterion is selected, its `display_name` and `excel_explanation` are already defined. Reuse them verbatim. Do not ask the user to redefine those two values unless the user explicitly says they want to change the reusable bank definition.

The user can select any subset.

The criterion bank is cumulative: as new criteria are defined in later projects, this list grows automatically.

## Step B — Ask whether to define additional criteria

After the built-in selection is confirmed, explicitly ask:

> Do you want to define any additional project-level criteria for this project?

If no, continue.

If yes, define each new criterion using the **Criterion Definition Contract** below.

After the user confirms a new criterion:

1. add it to `references/criteria-bank.md`;
2. assign/update its criterion version metadata;
3. save the bank;
4. include it in the current project's active criterion set if the user wants it active now.

Do not begin project analysis until every new criterion is fully defined **and persisted into the bank**.

---

# Criterion Definition Contract

Every new custom criterion must be reproducible.

Guide the user through the following information.

## Criteria-bank entry schema

Persist enough information that a future agent can apply the criterion without relying on the conversation in which it was created.

Each criterion entry must contain:

- `key` — stable machine-readable identifier;
- `version` — integer, starting at `1`;
- `status` — normally `active`;
- `display_name` — exact Excel criterion name;
- `aliases` — optional alternate names;
- `purpose`;
- `excel_explanation` — canonical `הסבר הקריטריון`;
- `scope`;
- `applicability`;
- `required_sources`;
- `required_observations`;
- `cache_fact_fields` — optional canonical atomic fact names that can satisfy the observations from the ingestion cache;
- `score_range`;
- `scoring_rule`;
- `boundary_and_tie_rules`;
- `allow_decimal_scores`;
- `not_applicable_rule`;
- `missing_evidence_rule`;
- `score_explanation_rule`;
- `score_explanation_examples`;
- `overlap_with_other_criteria`;
- `dependencies`;
- `notes`.

Do not add a criterion to the bank with only a name and score description.

## 1. Identity

Collect:

- **Display name** — the exact value to store in Excel under `שם הקריטריון`.
- **Internal key/name** — a stable internal identifier if the environment supports one.
- **Short purpose** — one sentence describing what the criterion is intended to measure.

## 2. Excel metadata

Collect the exact generic text for:

- `שם הקריטריון`
- `הסבר הקריטריון`

`הסבר הקריטריון` must describe the criterion itself, not one apartment.

For an existing bank criterion, do **not** generate either Excel metadata value from scratch. Copy `display_name` and `excel_explanation` exactly from the selected bank entry. They must remain identical for that criterion key/version across every apartment row and across every new project that uses it.

For a brand-new criterion, the values confirmed during definition become canonical immediately after they are persisted to the bank.

### Explanation style — mandatory

Keep both explanation fields **short, simple, and easy to scan**:

- `הסבר הקריטריון` — one short sentence that says only what the criterion measures. Avoid implementation details, scoring rules, examples, or long lists.
- `הסבר הציון` — a short phrase or one short sentence containing only the decisive apartment-specific evidence that caused the score.
- Use plain, concrete language. Avoid technical jargon when a simpler phrase works.
- Do not repeat the criterion definition inside `הסבר הציון`.
- **Special rule for `מיקום בקומה` and `שקט`/`רעש`: when the score is 0–6, `הסבר הציון` must name the exact verified cause of the low score in a few words.** Do not write vague text such as `מיקום פחות טוב` or `רועש`. State the cause itself, for example `סלון צמוד לפיר מעלית`, `צמוד לחדר אשפה`, `פונה לכביש ראשי`, or `ליד רמפת חניה`.
- For those two criteria, scores 7–10 may use a minimal positive/neutral explanation; the detailed cause requirement is primarily for low scores.
- Do not write reasoning chains or paragraph-length explanations in either Excel field.

Good examples:

- `מודד את מספר החזיתות החיצוניות.`
- `2 חזיתות חיצוניות`
- `חדר שינה צמוד למעלית`
- `כ-75 מ' מהחניה לבניין`

## 3. Scope

Determine what the criterion evaluates:

- apartment;
- floor;
- building;
- plot/site;
- parking/storage;
- or a combination.

Also determine whether the criterion is applicable:

- to every apartment;
- only to specific apartment types;
- only to specific floors;
- only when a feature exists.

## 4. Required evidence

Define exactly what the agent must inspect to calculate the criterion.

Possible sources include:

- individual apartment plan;
- typical floor plan;
- site/development plan;
- parking plan;
- storage plan;
- section/elevation;
- spec booklet;
- project listing;
- user-provided external context.

List every raw observation needed.

When possible, also define `cache_fact_fields`: stable atomic field names that the ingestion companion should look for in `derived/facts.json`. Reuse an existing field name from the cache contract when it represents the same fact; create a new field only when the observation is genuinely new. This makes future rescoring/refactoring deterministic and cheap.

Example:

- which room touches an elevator shaft;
- number of true exterior facades;
- direction of balcony;
- distance to parking;
- whether the apartment faces a school.

## 5. Scoring scale

Define:

- numeric range — normally `0–10`;
- exact meaning of high versus low;
- explicit score bands or formula;
- tie/boundary rules;
- whether half points/decimals are allowed.

Do not accept a vague rule such as "better apartment gets a higher score."

The rule must be sufficiently precise that another agent can reproduce the result.

## 6. Not-applicable behavior

Define whether the criterion can be non-applicable.

Choose one explicit behavior:

- leave score blank and explain why; or
- use a specific numeric sentinel such as `0` **only when the downstream application already understands that semantic**.

Never assume `0` means N/A.

## 7. Missing/uncertain evidence behavior

Define what to do when required evidence cannot be verified.

Default:

- leave the score blank;
- write the uncertainty in `הסבר הציון`;
- surface it to the user.

Do not guess merely to fill the workbook.

## 8. Apartment-specific explanation rule

Define what `הסבר הציון` should contain.

It should identify the evidence that actually caused the score, using the shortest clear wording possible.

Keep it to a short phrase or one short sentence. Include only the decisive evidence; do not restate the criterion or narrate the full analysis.

Where useful, define short explanation templates.

Example:

- `חדר שינה צמוד לפיר מעלית`
- `2 חזיתות חיצוניות`
- `חניה באזור בניין אחר, כ-75 מ' הליכה`

## 9. Relationship to existing criteria

Check for overlap.

Ask/decide:

- Does this criterion duplicate part of `שקט`, `מיקום בקומה`, `פרטיות`, etc.?
- If it overlaps, should the overlapping factor be removed from another criterion?
- Is double-counting intentional?

If scoring logic of an existing criterion must change because of the new one, that is a **criterion refactor** and must be applied retroactively to previously analyzed apartments.

## 10. Criteria-bank persistence

Every approved criterion becomes part of the reusable skill.

There is no normal "project-only" criterion mode.

Before using the criterion:

1. create a stable criterion key;
2. create criterion version `1` for a brand-new criterion;
3. add its complete definition to `references/criteria-bank.md`;
4. mark it `active`;
5. record its Excel display name and generic explanation exactly; once stored, these are canonical and must be reused verbatim by future projects using that criterion version;
6. record evidence requirements, scoring logic, applicability, N/A behavior, uncertainty behavior, overlap rules, and score-explanation guidance;
7. save the updated bank.

The workbook still stores only the Excel-relevant metadata:

- criterion name;
- score;
- criterion explanation;
- score explanation.

The detailed reusable analysis logic lives in the criteria bank.

If the user later changes the definition of an existing bank criterion, do not silently replace its historical meaning. Increment its version and apply the migration/refactor workflow to the current project.

## Criterion confirmation

Before accepting the custom criterion, summarize it to the user as:

- name;
- generic explanation;
- applicability;
- evidence required;
- scoring rule;
- N/A rule;
- uncertainty rule;
- overlap/refactor implications.

Get confirmation before using it.

After confirmation, persist the entry into the criteria bank immediately.

---

# Changing criteria after analysis has started

Criteria are allowed to evolve.

There are two cases.

## Case A — Add a new criterion

When the user adds a criterion after one or more buildings have already been analyzed:

1. Pause analysis of new buildings.
2. Complete the Criterion Definition Contract.
3. Persist the new criterion into `references/criteria-bank.md` and save the bank.
4. Add one new 4-column criterion block immediately after the existing criterion blocks.
5. Preserve every existing fixed field, criterion block and score.
6. Populate the new criterion's:
   - `שם הקריטריון`;
   - `הסבר הקריטריון`
   for every existing apartment row.
7. Translate the new criterion's `required_observations` into atomic evidence needs.
8. Query the ingestion cache (`derived/facts.json`, reviewed page Markdown, and existing detail crops) for **every previously completed building**.
9. Reopen original source pages only for observations that are missing, stale, ambiguous, or insufficiently detailed; add newly verified observations back to the cache with evidence pointers.
10. Calculate the new score for every previously analyzed apartment where applicable.
11. Populate `הסבר הציון`.
12. Present retroactive results building by building for approval.
13. Save after each retrofitted building.
14. Only after all previously completed buildings are updated may forward analysis resume.

Do not default historical apartments to `10`, `0`, or any other score merely because the criterion did not exist previously.

## Case B — Change/refactor an existing criterion

If the user changes:

- evidence inputs;
- applicability;
- score bands;
- formula;
- N/A semantics;
- or overlap with another criterion,

then the criterion is version-changed.

Before touching project data:

1. increment the criterion version in `references/criteria-bank.md`;
2. preserve the prior version entry/history in the bank;
3. make the new version the active version for future projects.

For every already analyzed apartment:

1. recalculate that criterion from the cached atomic facts/evidence first;
2. reopen original source pages only if the necessary raw fact was not previously recorded, is stale, or is ambiguous;
3. persist any newly verified atomic observations back into the ingestion cache with evidence pointers;
4. show the user the before/after score and explanation for affected apartments;
5. update the workbook building by building;
6. do not alter unrelated criterion scores unless the refactor explicitly changes them.

The workbook must never contain a mixture of old and new scoring logic for the same criterion.

---

# New-project Excel generation

For every new project, after the active criterion set is confirmed, generate a fresh workbook in the **exact standard structure** below.

The canonical workbook seed bundled with this skill is:

`assets/project-template-reference.xlsx`

This asset is the approved clean project template and is the preferred source for every new project. Clone it; never use a populated workbook from a previous project as the starting template.

The bundled template contains the fixed columns, one placeholder 4-column criterion block, RTL/layout/formatting, and the `Lottery` sheet structure. Expand or contract only the criterion area to match the active criterion set. The `Apartments` sheet must contain **no link/source columns**.

If the template asset cannot be used, recreate the same schema exactly from this contract.

## Template expansion rules

When generating the project workbook from the bundled template:

1. keep the 13 fixed `Apartments` columns unchanged;
2. treat the template's `שם הקריטריון | ציון | הסבר הקריטריון | הסבר הציון` columns as a **single placeholder criterion block**;
3. create exactly one such 4-column block for every active criterion;
4. if more than one criterion is active, duplicate the placeholder block immediately after the previous criterion block, preserving its formatting;
5. if exactly one criterion is active, reuse the placeholder block as-is;
6. if zero criteria are explicitly approved, remove the placeholder block so `מחיר` is the final `Apartments` column;
7. do not create link/source columns of any kind;
8. do not add criterion-specific headers: every criterion block keeps the same four generic headers;
9. do not populate project data into the template asset itself; always work on a project copy.

## Sheet order

1. `Lottery`
2. `Apartments`

Do not add other sheets by default.

---

# `Lottery` sheet contract

## Columns

The first row contains exactly:

| Column | Header |
|---|---|
| A | `מספר הגרלה` |
| B | `שם פרויקט` |
| C | `שם קבלן` |
| D | `עיר` |
| E | `מספר דירות כולל` |

The user supplies the project data for this sheet.

If the values are already known when the workbook is generated, write them into row 2.

If not, create the structure and leave row 2 available for the user/project data.

Do not use `Lottery` as an analysis sheet.

When continuing an existing project, treat its project metadata as read-only unless the user explicitly asks to correct it.

---

# `Apartments` sheet contract

One row represents one apartment.

## Fixed fields

The first 13 columns are always exactly:

| Order | Header | Data type / meaning |
|---:|---|---|
| 1 | `מגרש` | Plot/lot number |
| 2 | `בניין` | Building number |
| 3 | `דירה` | Apartment number |
| 4 | `טיפוס` | Apartment type/code |
| 5 | `קומה` | Raw floor value; numeric when single-level, text when multi-level such as `13,14` |
| 6 | `חדרים` | Numeric room count, including values such as `4.5` |
| 7 | `שטח` | Numeric apartment area |
| 8 | `מרפסת` | Numeric balcony/terrace area |
| 9 | `מחסן` | Storage identifier |
| 10 | `שטח מחסן` | Numeric storage area |
| 11 | `חניות` | Numeric count of assigned parking spaces |
| 12 | `כיוון` | Verified direction text |
| 13 | `מחיר` | Numeric apartment price |

### Important floor rule

`קומה` is kept because it is important source data.

It is **not scored here**.

The downstream application uses the raw floor value to compute a user-specific floor score according to that user's preference profile.

---

# Dynamic criterion blocks

Immediately after the 13 fixed columns, create one 4-column block for each active criterion, in the exact project criterion order approved by the user.

Every block has exactly these headers:

1. `שם הקריטריון`
2. `ציון`
3. `הסבר הקריטריון`
4. `הסבר הציון`

Example with three active criteria:

```text
... מחיר |
שם הקריטריון | ציון | הסבר הקריטריון | הסבר הציון |
שם הקריטריון | ציון | הסבר הקריטריון | הסבר הציון |
שם הקריטריון | ציון | הסבר הקריטריון | הסבר הציון
```

Never encode criterion identity in the column header itself.

The headers stay generic; the criterion name is stored in the row data.

This makes the schema dynamically readable by downstream software.

## Criterion row data

For every apartment row and every active criterion:

- `שם הקריטריון` — exact canonical criterion display name.
- `ציון` — numeric score.
- `הסבר הקריטריון` — canonical generic explanation.
- `הסבר הציון` — apartment-specific reason/evidence.

The criterion name and generic explanation are **bank-controlled canonical values**, not project-generated text. For an existing bank criterion, they must match the selected bank entry exactly and remain identical across all rows and all new projects using that criterion version. Only `הסבר הציון` is apartment-specific. Both explanation fields must follow the mandatory short-and-simple explanation style above, but the agent must never re-shorten or rephrase an existing canonical `excel_explanation` during project execution.

---

---

# Workbook generation validation

Immediately after generating a new-project workbook, verify:

1. sheet order is `Lottery`, then `Apartments`;
2. `Lottery` has exactly the five standard headers;
3. `Apartments` starts with the 13 fixed headers in the exact order;
4. there is exactly one complete 4-column block per selected criterion;
5. every selected existing criterion uses the exact bank `display_name` and `excel_explanation` with no project-specific rewording;
6. there is no floor criterion block;
6. every criterion block uses the exact generic four headers;
7. `Apartments` has exactly `13 + (4 × active criterion count)` columns;
8. there are no link/source columns;
9. there are no weights or final-ranking columns;
10. there are no extra analysis sheets;
11. numeric fields use numeric cell types when data is added.

---

# Existing-project intake

When the user supplies an existing project workbook:

1. Read `Lottery`.
2. Inspect `Apartments`.
3. Detect criterion blocks by the repeating 4-header pattern.
4. Read criterion names from populated apartment rows.
5. Compare the workbook's active criteria with the built-in/custom project criterion definitions.
6. Detect whether:
   - the project is complete;
   - some buildings are complete;
   - some rows are partially scored;
   - a criterion was added but not retrofitted to all prior buildings.
7. Resume from the workbook as the source of truth.

Use `(מגרש, בניין, דירה)` as the apartment identity key.

Use `טיפוס` and `קומה` as sanity checks.

Never rely on spreadsheet row number as identity.

---

# Phase 0 — Source intake, preprocessing, and orientation

After criteria are confirmed and the workbook exists, collect whatever project sources are required by the active criteria.

Possible sources:

| Document | Typical use |
|---|---|
| Typical floor plans | Core proximity, facades, directions, units per floor |
| Individual apartment plans | Unit layout, balcony/yard orientation, detailed adjacency |
| Site/development plan | Building position and external exposures |
| Parking + storage plans | Parking assignment, parking anomaly, storage position |
| Cross-sections | Floor elevations/heights and atypical levels |
| Spec booklet / apartment list | Unit metadata, sizes, price, storage/parking assignment |
| Project/listing data | Source URLs and pre-populated apartment facts |

The selected criteria determine which documents are mandatory. A custom criterion can introduce additional evidence requirements.

## Phase 0A — Run the sibling ingestion skill

Load and follow the `architectural-document-ingestion` skill installed by this same plugin. Prefer explicit invocation as `$architectural-document-ingestion` when the host supports it.

Generate or reuse a project cache before repeated analysis. Default cache contents include:

- `manifest.json` — source hashes and per-page routing metadata;
- `index.md` — lightweight human-readable source/page index;
- `pages/<source-id>/pNNNN.md` — one Markdown page record;
- `previews/<source-id>/pNNNN.webp` — low-resolution discovery preview;
- `crops/` — reusable high-resolution detail crops created only as needed;
- `derived/facts.json` — normalized atomic facts with evidence pointers.

Do not regenerate unchanged source preprocessing. Source SHA-256 is the invalidation key.

## Phase 0B — Criterion-driven page routing

Use each active criterion's `required_sources` and `required_observations` to decide which pages need review. Do not deeply inspect unrelated drawings merely because they exist.

Examples:

- directions/facades/location on floor → typical floor + apartment plans;
- parking proximity → parking assignment source + parking plans;
- quiet/external exposure → site plan + relevant apartment/floor plan + external context when required;
- section-dependent criterion → only relevant sections/elevations.

Classify candidate pages from lightweight previews first. Escalate to the original page/crop only when necessary.

## Phase 0C — Source-format handling and resolution ladder

Files named `.pdf` can occasionally be image bundles or archives. Verify the actual format before processing.

For dense architectural drawings:

1. **Index level:** use cached WebP previews + page Markdown to identify title block, sheet subject, compass, buildings, apartment types, and candidate evidence.
2. **Page level:** open/render the relevant original PDF page when a criterion needs verified geometry/context.
3. **Detail level:** create a high-resolution crop directly from the original page when labels, dimensions, walls, openings, or parking marks are too small. Reuse that crop later.

Never upscale a low-resolution preview and treat it as authoritative detail evidence.

Inspect the title block, scale, north/compass, and sheet subject when relevant. Do not treat companion text/OCR as authoritative unless verified against the drawing.

## Phase 0D — Store reusable atomic facts

Whenever a project fact is verified, prefer storing the underlying observation in `derived/facts.json` instead of storing only a criterion score.

Examples:

- `exterior_facade_count = 2`;
- `primary_directions = [south, west]`;
- `elevator_adjacency_room = bedroom`;
- `units_on_floor = 4`;
- `parking_walking_distance_m = 42`;
- `west_edge_external_use = major_road`.

Every fact must reference its source id/page and, when useful, a crop. These atomic facts are the primary mechanism for efficient future criterion additions/refactors.

---

# Phase 1 — Project context

Collect project context required by the active criteria.

## Per plot / direction

When relevant, determine what lies in each direction:

- major road;
- minor road;
- local street;
- pedestrian path;
- park/green space;
- internal courtyard;
- neighboring residential building;
- commercial building;
- school/kindergarten/playground;
- bus stop;
- rail/light rail;
- gas station;
- restaurant/bar/noise venue;
- parking-garage ramp;
- open or blocked view.

## Per building

Record working facts such as:

- position in plot;
- number of floors;
- atypical floors;
- elevator count and shaft location;
- stairwell;
- service shafts;
- lobby/corridor;
- occupancy of lower levels;
- commercial space below/beside the building;
- number of apartments per relevant floor.

These facts support scoring but do not create extra Excel columns by default.

---

# Phase 2 — Per-building architectural analysis

Analyze one building completely before moving to the next.

## Identify building core

Locate:

- elevator shafts;
- stairwell;
- refuse chute;
- service/electrical/comms risers;
- floor lobby/corridor;
- storage/common/service rooms touching apartments.

## Collect/verify the fixed apartment fields

For each apartment:

- `מגרש`
- `בניין`
- `דירה`
- `טיפוס`
- `קומה`
- `חדרים`
- `שטח`
- `מרפסת`
- `מחסן`
- `שטח מחסן`
- `חניות`
- `כיוון`
- `מחיר`

Use numeric values for numeric fields.

Use the project's established direction representation.

## Collect scoring evidence

Depending on the active criteria, collect facts such as:

- true exterior facade count;
- room-to-elevator adjacency;
- room-to-refuse/service adjacency;
- stair/corridor adjacency;
- corner/interior position;
- external noise exposure;
- ground/private-yard condition;
- apartments per floor;
- parking location and walking distance;
- verified direction/orientation;
- custom-criterion observations.

A fact does not need its own Excel column to be valid evidence.

When it influences a score, capture it in `הסבר הציון`.

---

# Phase 3 — Parking analysis

Run only when needed by:

- an active parking criterion;
- missing fixed parking information; or
- explicit user request.

## Parking mapping

1. Read the authoritative apartment-to-parking assignment.
2. Locate building cores.
3. Locate the assigned spaces physically.
4. Do not infer physical area from parking-number range alone.

## Parking anomaly examples

- both spaces in another building's zone → severe;
- one space in another building's zone → moderate.

## Walking distance

When needed:

- calibrate from the printed plan scale;
- sanity-check against a known-size object;
- measure the practical route, not only straight-line distance;
- state approximate visual-measurement error.

Do not add a new raw-distance column unless the user changes the workbook contract.

---

# Phase 4 — Cross-sections

When relevant, use printed elevation marks rather than pixel measurement.

Watch for:

- obscured marks;
- ambiguous digits;
- unusual upper-floor heights;
- basement levels.

Store findings as analysis evidence unless an active criterion explicitly needs them.

---

# Criteria bank runtime loading

The authoritative reusable criterion definitions live only in:

`references/criteria-bank.md`

Do **not** maintain a second mirrored set of criterion definitions inside `SKILL.md`. The bank is intentionally cumulative and must be able to grow from project to project without requiring duplicate edits elsewhere.

Whenever criterion logic is needed:

1. load the current `references/criteria-bank.md`;
2. resolve the criterion by its stable `key` / canonical `display_name`;
3. use the latest active version for a new project unless the user explicitly selects another project convention, and copy that version's `display_name` and `excel_explanation` verbatim into the workbook;
4. for an existing workbook, preserve its established version/convention unless the user requests a refactor;
5. if a bank criterion is changed, version it and run the retrofit/refactor workflow before continuing forward analysis.

Floor/Floor Preference remains excluded from the bank as a built-in project-level criterion. Raw `קומה` stays in the fixed fields and personalized floor scoring remains downstream.

---

# Phase 5 — Building scoring

For every active criterion:

1. verify applicability;
2. map `required_observations` to cached atomic facts;
3. reuse verified facts/crops when sufficient and reopen original source pages only for missing/ambiguous evidence;
4. add newly verified atomic observations back to the ingestion cache;
5. apply the confirmed criterion definition;
6. write a numeric score only when the evidence supports it;
7. write the canonical `display_name` and `excel_explanation` exactly as stored in the selected bank criterion version;
8. write apartment-specific evidence in `הסבר הציון`.

Do not invent a score to make the row complete.

---

# Phase 6 — Building completion and Excel write-back

## Completion gate

A building is ready when:

- all apartments in scope are identified;
- fixed fields are collected/verified as far as the sources allow;
- every active criterion has been evaluated;
- every populated score has a score explanation;
- unresolved evidence is explicitly identified.

## Approval presentation

Show a compact building table containing at least:

- plot;
- building;
- apartment;
- type;
- floor;
- each active criterion score;
- short score explanation;
- unresolved uncertainties.

Do not invent a weighted final score; this workbook does not contain one.

## Apartment row matching

Use:

`(מגרש, בניין, דירה)`

Then sanity-check:

- `טיפוס`;
- `קומה`.

If duplicate identity keys exist, do not write that building until the conflict is surfaced.

## Write rules

For the approved building:

1. update only that building;
2. fill verified fixed fields;
3. populate every active criterion block;
4. append any missing apartment rows using the exact workbook schema;
5. do not modify `Lottery`;
6. do not modify unrelated buildings.

## Incremental workbook requirement

The workbook must be built progressively, one completed building at a time:

1. complete the current building analysis;
2. present it for approval unless that approval step was explicitly waived;
3. immediately write **all apartments from that building** into the project Excel workbook;
4. validate the just-written building;
5. save the workbook to disk;
6. only after the save succeeds may analysis begin on the next building.

Do not wait until all buildings are analyzed before populating Excel. Do not keep a completed building only in temporary analysis/cache data. Every saved checkpoint must contain all previously completed buildings plus the newly completed building.

## Save checkpoint

Save the workbook immediately after the building is written and validated.

The saved workbook becomes the source of truth before analyzing the next building.

---

# Per-building validation

After every write, verify:

1. every expected apartment has exactly one row;
2. no duplicate `(מגרש, בניין, דירה)` key was created;
3. numeric fixed fields are numeric;
4. `חדרים` values such as `4.5` remain numeric;
5. multi-level `קומה` values may remain text;
6. every populated criterion score is numeric;
7. every score is inside that criterion's valid numeric range;
8. every populated score has `הסבר הציון`;
9. both `הסבר הקריטריון` and `הסבר הציון` are short, simple, and contain no unnecessary detail;
10. `שם הקריטריון` is consistent across the entire criterion block;
11. `הסבר הקריטריון` is consistent across the entire criterion block;
12. there is no floor criterion block;
13. there are no link/source columns;
14. no unrelated building changed;
15. `Lottery` is unchanged;
16. the saved workbook already contains every previously completed building plus the current building.

---

# Criteria consistency audit

Before declaring the project complete:

1. enumerate all active criterion blocks;
2. verify each apartment has the same criterion block order;
3. verify no building was left on an old criterion definition;
4. verify any newly added criterion was retrofitted to all completed buildings;
5. verify any criterion refactor was recalculated across all affected apartments;
6. verify the workbook contains no mixed old/new scoring logic;
7. verify all unresolved blanks are explainable rather than accidental omissions.

---

# Project data versus personalized ranking

## Layer 1 — Project data

Stored in this workbook:

- fixed apartment facts;
- selected shared criterion scores;
- generic criterion definitions;
- apartment-specific score explanations.

## Layer 2 — User profile

Not stored in this workbook:

- criterion weights;
- user-specific floor preference;
- personal direction preference if handled by the application;
- budget;
- apartment-size filters;
- must-haves;
- personal exclusions.

## Layer 3 — Computed ranking

Derived by the application from Layer 1 + Layer 2.

This allows the expensive architectural analysis to be performed once while different users receive different rankings.

---


# Criteria-bank maintenance audit

At the end of any session that introduced or changed criteria, verify:

1. every approved new criterion exists in `references/criteria-bank.md`;
2. every existing criterion written to Excel matches its selected bank version's canonical `display_name` and `excel_explanation` exactly;
3. its full definition is present, not only its name;
4. new criteria have a stable key and version;
5. changed criteria have a new version rather than silently overwriting historical logic;
5. the active bank version is the version used by the current project after retrofit;
6. every active bank criterion can be presented during the next new-project criteria-selection phase;
7. Floor/Floor Preference is still excluded from the project-level criteria bank unless the user explicitly reintroduces it as a distinct shared criterion.


# Deliverables

Primary deliverable:

1. Updated project Excel workbook in the exact standard structure, checkpointed building by building.

When starting a brand-new project:

2. Fresh standard workbook generated after criterion selection.

Supporting deliverables when requested:

3. Project ingestion/evidence cache (`manifest.json`, page Markdown, previews/crops, derived facts).
4. Building-by-building analysis summary.
5. Findings/anomaly report.
6. Criterion retrofit/refactor comparison.
7. User-specific ranking generated downstream from the project data plus a user profile.

Always state important limits:

- architectural documents can contain errors;
- visual distance measurements are approximate;
- uncertain evidence must remain identified;
- the project dataset informs ranking but does not replace verification of authoritative source documents.
