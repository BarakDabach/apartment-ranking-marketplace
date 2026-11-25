# Guided DWF ingestion

Use this workflow when a user wants to guide extraction from a 2D DWF through
Autodesk Design Review. The objective is a small agreed document map followed by
evidence-backed extraction with explicit approval boundaries.

## Intake

Ask one concise question at a time. Accept `unknown`; do not force the user to
answer information they do not have.

Collect:

1. Project name, city, lot number, and lottery number when known.
2. Building count and the exact building identifiers used in the drawings.
3. Design Review sheet numbers containing relevant floor plans, and whether a
   sheet is organized per floor, per building, or contains multiple plans.
4. Floors, repeated typical-floor ranges, and special floors such as garden,
   entrance, duplex, penthouse, and roof.
5. Sheet numbers for the complete lot/site/surroundings plans.
6. Sheet numbers for parking/garage and storage plans.
7. Location and organization of apartment schedules or detail tables.
8. Apartment/type numbering conventions, units, and known mirrored types.
9. Known apartment totals per floor, building, or project for completeness
   checks.
10. North-arrow or project-orientation rules. If direction cannot later be
    established from authoritative drawing evidence, ask the user rather than
    infer it.
11. Required output fields, exclusions, and the desired approval boundary for
    repeated plans.

## Agreement gate

Before controlling Design Review or extracting normalized data, restate the
understanding as a compact map:

```text
sheet -> building -> floor/range -> expected apartments -> related site/parking/storage evidence
```

Include assumptions and unresolved items. Wait for the user's explicit
confirmation or corrections. Agreement authorizes only the described extraction
scope, not unrelated sheets or external actions.

## Extraction and approvals

Navigate only the agreed sheets. Preserve a full-sheet capture for coverage,
then zoom or crop from the authoritative source for detail evidence. Every
normalized field must retain its source sheet/region and confidence.

- If plans are organized per floor, finish one floor and pause for manual
  approval before starting the next floor.
- If plans are organized per building, finish one building and pause for manual
  approval before continuing.
- Treat a repeated typical-floor range as one layout only when the drawing and
  the agreed map explicitly say it repeats; preserve the covered floor range.
- Ask when orientation is absent or ambiguous.
- Never silently convert uncertain OCR into an accepted field.

## DWF data rules

- DWF drawings are not an authoritative price source. Leave `price` empty and
  never infer it. Add price only from a separate authoritative source explicitly
  supplied for that purpose.
- Populate `storageNumber` only when drawing evidence correlates the apartment
  to that storage unit.
- Populate `storageAreaSqm` only when both the apartment-to-storage correlation
  and the size of that same storage unit are evidenced. An unassociated storage
  schedule is not enough; retain it only as an unresolved observation.
- Apply the same evidence rule to apartment-to-parking assignments. A parking
  number alone does not establish ownership.

## Verification

At each approval checkpoint report:

- source sheet and reviewed region;
- building and floor/range;
- extracted apartment count versus any expected count;
- fields accepted, left blank, or in conflict;
- unresolved orientation, parking, and storage correlations;
- evidence links needed to reproduce the decision.

Do not continue past a required checkpoint until the user approves or corrects
the result.

## Dry-run mode

When the user asks for a dry run, perform only the intake and agreement gate.
Demonstrate the questions one at a time and produce the proposed document map,
but do not control Design Review, extract data, or modify project records.
