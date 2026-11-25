# Apartment Ranking — Criteria Bank

This file is the persistent reusable criterion registry for the `apartment-ranking` skill.

## Rules

- Every approved new project-level criterion must be added here.
- Every criterion must contain enough analysis detail to be reproducible in a future project.
- Presence in the bank means "supported by the skill", not "automatically active for every project".
- The user chooses active criteria at the beginning of every new project.
- Do not add Floor / Floor Preference as a project-level criterion. Raw `קומה` is stored in Excel and ranked later per user in the application.
- When an existing criterion changes semantically, increment its version and preserve the prior version definition/history.
- New projects use the latest active version unless the user explicitly requires an older project convention.
- This file is the **single source of truth** for reusable criterion definitions. Do not duplicate the full criterion definitions in `SKILL.md`.
- When adding a criterion, preserve the same field schema used by the existing entries: stable key/version/status, Excel metadata, scope/applicability, required evidence, numeric scoring logic, N/A and missing-evidence behavior, score-explanation rules, overlap/dependencies, and notes.
- `excel_explanation` is one clear sentence describing what the criterion measures (detailed wording is allowed and is canonical once stored). Generated `הסבר הציון` text must be a short phrase or one short sentence with only the decisive evidence.
- `display_name` and `excel_explanation` are **canonical cross-project metadata**. For any project using an existing criterion version, copy both values verbatim from this bank. Do not paraphrase, translate, shorten, expand, or otherwise adapt them to the project.
- Once a new criterion is confirmed and added here, its `display_name` and `excel_explanation` become the canonical values for all future projects using that version.
- If the user explicitly requests a change to a criterion name or generic description, update/version this bank entry first. Do not create a silent project-only variant by default.

---

## Criterion: Quiet

- **key:** `quiet`
- **version:** `3`
- **status:** `active`
- **display_name:** `שקט`
- **aliases:** Quiet; רעש
- **purpose:** Measure expected exposure to identifiable external and internal project noise sources.
- **excel_explanation:** `מודד את רמת החשיפה הצפויה של הדירה למקורות רעש שניתן לזהות מתכניות הפרויקט, כגון כבישים, מסחר, חניונים, חצרות, מעליות ופירים.`
- **scope:** apartment + building + plot/site
- **applicability:** normally all apartments
- **required_sources:** site/development plan, typical floor plan, neighborhood overview map/aerial when available (for off-plot exposures); other sources as needed
- **required_observations:** road/rail/commercial/playground/garage-ramp exposure; every public facility in the external noise-source checklist (case_rules v3); elevator/refuse/service adjacency; floor-height noise attenuation if used
- **cache_fact_fields:** `road_exposure`, `rail_exposure`, `commercial_exposure`, `playground_exposure`, `public_facility_exposure`, `garage_ramp_exposure`, `elevator_adjacency_room`, `refuse_or_service_adjacency`, `floor`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** start from 8 and apply only verified effects; clamp to 0–10
- **fallback_adjustments:**
  - major road: -3
  - rail: -3
  - minor road: -2
  - bus stop: -2
  - retail: -2
  - noise venue: -2
  - garage ramp: -2
  - school: -1
  - playground: -1
  - local street: -1
  - park/courtyard/green: 0
  - neighboring residential: 0
  - below grade: -1
  - ground: -1
  - floors 1–3: 0
  - floors 4–12: +1
  - above 12: +2
  - living room on elevator: -2
  - bedroom on elevator: -1
  - refuse chute: -2
  - commercial storage: -2
  - resident storage: -1
- **case_rules (v2):**
  - garage ramp (-2) applies only when an apartment facade is above or on the edge of an open ramp; verify by aligning the ground/site plan with the typical floor on a fixed core element (e.g. elevator shafts). Covered/underground internal ramps between basement levels: 0.
  - open garage ramp facing the facade at ~5–15 m, not at the facade edge, with a paved/garden strip in between (e.g. fire pad + garden): -1 (reduced ramp exposure; does not stack with the -2 ramp rule). Beyond ~15 m or with a building in between: 0.
  - refuse chute/room (-2) applies only when the apartment shares a wall with the refuse room or chute. Refuse room behind shafts with no shared wall: 0. Detached refuse-chute outlet bins or containers in the garden: 0.
  - pedestrian/bike paths inside a public park: 0 (part of park/green). Fire-truck access pad: 0.
  - emergency generator room on a lower floor (slab contact, no shared wall): 0; mention it only as a note.
  - local street with parking bays: -1 (local street).
- **case_rules (v3):**
  - off-plot exposures: verify each facade against the neighborhood overview map/aerial; a road outside the plot boundary that is missing from the plot site plan still counts.
  - neighborhood spine/collector road (runs across the neighborhood, roundabouts at its ends/intersections), facing the facade within ~30 m: minor road -2. Short dead-end/local access street with parking bays: local street -1. Perimeter arterial/highway: major road -3.
  - surface parking street (lane with perpendicular/parallel stalls) directly facing the facade: local street -1. If the street starts beyond the building footprint line (only diagonal view): 0.
  - public playground or outdoor fitness area in an adjacent park, facing the facade within ~50 m with no building in between: playground -1. Farther or screened by a building: 0.
  - pedestrian promenade / boulevard path without vehicles: 0.
  - distant facilities (retail strip, schools, health clinic, synagogue, day care, stadium) more than ~100 m away or behind other buildings: 0; mention only if notable.
  - **external noise-source checklist (mandatory scan):** for every building, scan the site plan, the neighborhood overview map (read its legend/icons) and any aerial rendering for ALL of the source types below, record each one found near the building as a fact (type, side, approx. distance, whether a building is in between), and apply the mapped adjustment only to facades that face it within the distance limit with no building in between:
    | source type | mapped adjustment | distance limit |
    |---|---|---|
    | highway / perimeter arterial | major road -3 | ~50 m |
    | neighborhood spine/collector road, roundabout, signalized junction | minor road -2 | ~30 m |
    | local street, parking street, surface parking lot | local street -1 | facing directly |
    | bus stop / bus terminal | bus stop -2 | ~30 m |
    | railway / light rail | rail -3 | ~100 m |
    | retail strip, mall, ground-floor shops, gas station | retail -2 | ~50 m |
    | stadium, sports arena, event hall, restaurant/bar/nightlife | noise venue -2 | ~100 m (stadium: ~300 m) |
    | school, kindergarten, day care (מעונות יום), community center (מתנ"ס) | school -1 | ~50 m |
    | synagogue / place of worship | school -1 | ~50 m |
    | public playground, outdoor fitness area, sports court/field, dog park | playground -1 | ~50 m |
    | health clinic (קופת חולים) and other public buildings | 0 (or local street -1 if its parking/drop-off faces the facade) | facing directly |
    | public park, lawn, pedestrian promenade, park paths | 0 | — |
    | open garage ramp, public parking garage entrance | garage ramp -2 | facade above/at edge |
    | open garage ramp, not at edge | -1 | ~5–15 m, facing directly |
    | transformer room / electrical substation (טרפו) | -1 | shared wall or grilles/doors within ~10 m of the facade; beyond ~10 m: 0 |
    | detached underground refuse containers (red circles on site plan) | 0 | refuse rule applies only with a shared wall; ~10 m+ in the plaza = 0 |
    | sealed void (חלל אטום) adjoining the unit | 0 | not a refuse room or shaft; verify the label before applying a refuse/shaft deduction |
    | utility meter cabinets in the lobby wall (מים / חשמל / גז) | 0 | passive closets, not service/smoke shafts; no location or quiet reduction |
  - each distinct source type counts once per apartment (do not stack the same road on two facades); different source types stack.
  - the building's own entrance plaza and the plot's internal paved plaza (including a hatched fire-truck pad): 0.
  - shared residents' courtyard pergola/seating area and garage ventilation shaft/grille in the garden more than ~10 m from the facade: 0 (courtyard). A ventilation grille directly below/at the facade (<~5 m): treat as garage ramp -2 only if it is an exhaust outlet; otherwise note only.
  - a source type that is not in this checklist must be added here (with its mapped adjustment) before it is used for scoring.
- **boundary_and_tie_rules:** apply only verified factors; cap final score to range
- **not_applicable_rule:** normally applicable
- **missing_evidence_rule:** leave score blank and explain uncertainty
- **score_explanation_rule:** keep it short. If score is 0–6, state the exact verified noise cause(s) that lowered the score; never use a generic label like `רועש`. For scores 7–10, a minimal positive/neutral explanation is enough.
- **score_explanation_examples:** low: `פונה לכביש ראשי`; `ליד רמפת חניה`; `חדר שינה צמוד לפיר מעלית`; combined only when needed: `מזרח לכביש ראשי | קומה נמוכה`. high: `ללא מקור רעש משמעותי`
- **overlap_with_other_criteria:** elevator/core adjacency may also affect Location on Floor; keep distinctions explicit
- **dependencies:** none
- **notes:** floor here is only a noise attenuation factor, not personal floor preference
- **version_history:** v1 = same scoring_rule and fallback_adjustments without the v2 case_rules (refuse/ramp penalties were not restricted to shared wall / open-ramp exposure). v2 added from project 2181 (שמורת אלמוגים – חיפה). v3 (same project) added off-plot verification against the neighborhood overview map and rules for spine roads, parking streets, public playgrounds/fitness areas, promenades and distant facilities, plus the mandatory external noise-source checklist (synagogues, kindergartens/day care, community centers, sports courts, dog parks, bus stops, gas stations, clinics etc. mapped to existing adjustment values); scoring values unchanged. v3.1 (same project, B6) added the open ramp at ~5–15 m (not at edge) = -1 case. v3.2 (same project, B8) added the transformer room (טרפו) case: -1 within ~10 m / shared wall, else 0. v3.3 (same project, B10) added the sealed void (חלל אטום) = 0 case. v3.4 (same project, C14) added lobby utility meter cabinets = 0.

---

## Criterion: Location on Floor

- **key:** `location_on_floor`
- **version:** `2`
- **status:** `active`
- **display_name:** `מיקום בקומה`
- **aliases:** Location on floor
- **purpose:** Measure apartment position relative to building core and shared circulation/service elements.
- **excel_explanation:** `מודד את איכות מיקום הדירה בתוך הקומה ביחס לגרעין הבניין, מעליות, חדרי מדרגות, פירים, מעברים ודירות סמוכות.`
- **scope:** apartment + floor
- **applicability:** normally all apartments
- **required_sources:** typical floor plan, apartment plan when needed
- **required_observations:** corner/interior position; elevator contact; refuse/service-riser contact; stair/corridor adjacency; isolation from core
- **cache_fact_fields:** `position_on_floor`, `core_adjacency`, `elevator_adjacency_room`, `refuse_or_service_adjacency`, `stair_adjacency`, `corridor_adjacency`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** fallback baseline corner=8, interior=6; overrides: living room on elevator=4, refuse chute=4, service riser=5, bedroom on elevator=6, stairwell only=7; well-isolated may receive +1 up to 10
- **case_rules (v2):** any shared wall with a space that can produce noise reduces the score:
  - shared wall with the floor lobby/corridor: -1 from baseline (corner 7, interior 5)
  - shared wall with smoke-exhaust, pressurization, compaction or other fire/service shafts: treat as service riser = 5
  - shared wall with a shared amenity (residents' club, gym), including through bathrooms/service rooms: -1 on top of the otherwise applicable score (e.g. stairwell 7 -> 6)
  - refuse room/chute counts only with a shared wall
  - an open kitchen that is part of the living space counts as the living room for elevator adjacency (living room on elevator = 4; Quiet -2)
  - plumbing/architectural shafts that adjoin only wet rooms (bathroom, WC, laundry): 0. An unlabeled shaft that adjoins a living space or bedroom: verify its type from other floors/sections; if it is smoke-exhaust/fire/service, treat as service riser = 5; if the type cannot be determined, do not reduce the score (mention the unlabeled shaft in the explanation only)
- **boundary_and_tie_rules:** actual room/core geometry takes precedence over generic corner/interior classification
- **not_applicable_rule:** normally applicable
- **missing_evidence_rule:** leave score blank
- **score_explanation_rule:** keep it short. If score is 0–6, state the exact verified floor-position cause that lowered the score; never use a generic label like `מיקום פחות טוב`. For scores 7–10, a minimal positive/neutral explanation is enough.
- **score_explanation_examples:** low: `סלון צמוד לפיר מעלית`; `צמוד לחדר אשפה`; `צמוד למעבר משותף`. high: `דירת פינה, רחוקה מהגרעין`
- **overlap_with_other_criteria:** some core adjacency can also affect Quiet
- **dependencies:** none
- **notes:** check ground/first floors separately: amenity rooms (club, gym) often replace an apartment slot there
- **version_history:** v1 = same scoring_rule without the v2 case_rules (no lobby, shaft-type or amenity-wall adjustments). v2 added from project 2181 (שמורת אלמוגים – חיפה).

---

## Criterion: Direction Quality

- **key:** `direction_quality`
- **version:** `1`
- **status:** `active`
- **display_name:** `איכות כיוון`
- **aliases:** Direction quality
- **purpose:** Measure shared project-level direction quality using a declared climate/orientation convention.
- **excel_explanation:** `מודד את איכות כיווני הדירה לפי חשיפה לשמש, אקלים מקומי ואופי הפתחים העיקריים, בהתאם לסולם הכיוונים שהוגדר לפרויקט.`
- **scope:** apartment
- **applicability:** apartments with verifiable exterior orientation
- **required_sources:** apartment plan / typical floor plan with verified compass
- **required_observations:** orientation of primary living/balcony/bedroom openings
- **cache_fact_fields:** `primary_directions`, `balcony_direction`, `bedroom_directions`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** Mediterranean/northern-hemisphere fallback: S=10, SE=9, SW=8, E=8, NE=7, W=6, NW=6, N=6
- **boundary_and_tie_rules:** project convention must be declared before analysis; drawing orientation overrides marketing text
- **not_applicable_rule:** blank if orientation cannot be verified
- **missing_evidence_rule:** leave score blank
- **score_explanation_rule:** state verified directions and the project convention used
- **score_explanation_examples:** `כיוון עיקרי דרום-מזרח`
- **overlap_with_other_criteria:** avoid using road/noise exposure here when it is already part of Quiet
- **dependencies:** declared project climate/orientation convention
- **notes:** can be user-sensitive; only keep as project criterion when the project has a shared convention

---

## Criterion: Facades

- **key:** `facades`
- **version:** `1`
- **status:** `active`
- **display_name:** `כמות חזיתות`
- **aliases:** Facades
- **purpose:** Measure the number of true exterior apartment facades.
- **excel_explanation:** `מודד את מספר החזיתות החיצוניות של הדירה לפי התכנית; יותר חזיתות עשויות לאפשר יותר פתחים, אור טבעי ואוורור.`
- **scope:** apartment
- **applicability:** normally all apartments
- **required_sources:** typical floor plan / apartment plan
- **required_observations:** every apartment boundary wall and whether it is a true exterior facade with relevant openings
- **cache_fact_fields:** `exterior_facade_count`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** fallback: 4 facades=10, 3=9, 2=7, 1=5, 0=3
- **boundary_and_tie_rules:** shared/core/corridor walls do not count; inner recesses, light-well walls and laundry/service notches (משטח מנגב) are not separate facades — count only true exterior building faces. A face whose only openings belong to service rooms (WC, bathroom, laundry niche) does not count and its direction is not listed in כיוון. A window that opens into a shallow notch (open on one side only) is a recess window, not a facade. A side facing a narrow sunken planter/light trench (~1 m) does not count; the same applies to a below-grade window into a narrow English courtyard (~1.5–2 m, retaining wall opposite).
- **not_applicable_rule:** normally applicable
- **missing_evidence_rule:** leave score blank
- **score_explanation_rule:** state verified facade count
- **score_explanation_examples:** `2 חזיתות חיצוניות`
- **overlap_with_other_criteria:** none
- **dependencies:** none
- **notes:** exterior-wall interpretation must be verified visually

---

## Criterion: Privacy

- **key:** `privacy`
- **version:** `1`
- **status:** `active`
- **display_name:** `פרטיות`
- **aliases:** Privacy
- **purpose:** Measure planning conditions that materially affect apartment privacy.
- **excel_explanation:** `מודד מאפייני תכנון המשפיעים על פרטיות הדירה, בעיקר בדירות קרקע/גן או בדירות החשופות לשטחים משותפים וציבוריים. בדירה רגילה שאינה בקומת קרקע הקריטריון עשוי לא להיות משוקלל.`
- **scope:** apartment + immediate surroundings
- **applicability:** project-dependent; commonly relevant to ground/garden/special apartments
- **required_sources:** apartment plan, site/development plan, adjacent-use plans
- **required_observations:** private yard/terrace, adjacency to public/shared/commercial/service areas, exposure
- **cache_fact_fields:** `garden_or_private_yard`, `terrace`, `adjacent_external_use`, `shared_area_exposure`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** fallback examples: garden/private yard=7; garden adjacent commercial storage=4; ground private yard=7; garden duplex=7; penthouse large terrace=5
- **boundary_and_tie_rules:** project convention determines whether standard apartments are N/A
- **not_applicable_rule:** prefer blank unless downstream system explicitly defines numeric sentinel semantics
- **missing_evidence_rule:** leave score blank
- **score_explanation_rule:** cite the privacy-affecting planning condition
- **score_explanation_examples:** `קומת קרקע + חצר פרטית`; `חצר צמודה לשטח שירות משותף`
- **overlap_with_other_criteria:** may overlap with noise/circulation; avoid double-counting unless intentional
- **dependencies:** project N/A convention
- **notes:** never assume 0 means N/A

---

## Criterion: Units per Floor

- **key:** `units_per_floor`
- **version:** `1`
- **status:** `active`
- **display_name:** `כמות דירות`
- **aliases:** Units per floor
- **purpose:** Measure shared-floor density.
- **excel_explanation:** `מודד כמה דירות חולקות את אותה קומה ואת אזורי הגישה המשותפים; פחות דירות בדרך כלל משמעותן פחות תנועה ויותר שקט ופרטיות.`
- **scope:** floor / apartment
- **applicability:** normally all apartments
- **required_sources:** typical floor plan
- **required_observations:** count of apartments sharing the relevant floor/common access area
- **cache_fact_fields:** `units_on_floor`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** 1–2=10, 3=9, 4=7, 5=5, 6=3, 7=2, 8+=1
- **boundary_and_tie_rules:** duplexes require explicit shared-access-floor handling
- **not_applicable_rule:** normally applicable
- **missing_evidence_rule:** leave score blank
- **score_explanation_rule:** state the apartment count on the relevant floor
- **score_explanation_examples:** `3 דירות בקומה`
- **overlap_with_other_criteria:** can indirectly relate to Quiet/Privacy but represents density specifically
- **dependencies:** none
- **notes:** none

---

## Criterion: Parking Proximity

- **key:** `parking_proximity`
- **version:** `2`
- **status:** `active`
- **display_name:** `קרבת חניה`
- **aliases:** Parking proximity
- **purpose:** Measure convenience of reaching assigned parking from the apartment's building/core.
- **excel_explanation:** `מודד את נוחות הגישה מהחניה המשויכת לדירה אל גרעין הבניין, תוך התחשבות במרחק הליכה, מפלס החניה וחריגות שבהן החניה נמצאת באזור של בניין אחר.`
- **scope:** apartment + parking + building
- **applicability:** apartments with assigned parking
- **required_sources:** parking/storage assignment table (e.g. ג'4 lottery appendix: parking numbers + level per apartment) and parking level plans (common-area plans)
- **required_observations:** assigned-space location, nearest building/core, practical walking route, level, anomaly
- **cache_fact_fields:** `assigned_parking_id`, `parking_building_zone`, `parking_walking_distance_m`, `parking_level`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** distance fallback: <30m=9, 30–45=7, 45–60=6, 60–75=4, 75–90=3, 90–105=2, >105=1; normal close/non-anomalous assignment may be 10 when project convention supports it
- **measurement_rule (v2):**
  - calibrate the drawing scale from dimension annotations written on the same sheet (storage/room dimensions in cm) and cross-check with a standard stall depth (~5.0 m) and aisle (~6.0 m); do not trust the printed sheet scale without this check.
  - measure the practical walking route (not straight line) from the elevator lobby of the apartment's own building core on the parking level to the nearest walkable point of the assigned stall group; do not route over vehicle ramp slopes or through walls.
  - multiple stalls / tandem pair: measure to the nearest walkable point of the group; tandem may be mentioned briefly.
  - parking reachable only via another building's core or outdoors: measure that actual route.
  - round distances to the nearest ~5 m and write them as approximate (`כ-`); score the rounded value so score and explanation agree.
  - routing on vector plans: walls (outlines, columns, wall hatch) are a high-penalty but passable mask, because door openings are often drawn closed by thresholds/leaves/text; report the geometric path length, not the penalized cost.
- **case_rules:**
  - mixed parking levels for one apartment (e.g. `(-2),(-1)`): locate each stall on its level; score by the nearest stall.
  - parking id written as a range (e.g. `115-120`): treat as the listed group; verify on the plan, never assume.
  - stall numbers drawn as vector stroke glyphs (not text): decode per plot (templates differ by plot/drafter, labels may be rotated 90°/180°/270°); stalls not decoded are located manually with a crop.
  - 180°-rotated stall labels: decoders swap 6↔9 (e.g. 60 read as 90, 126 as 129). Accept a swapped reading only when consecutive neighbour numbers sit next to it; an id decoded at two places is resolved by the neighbour sequence. Interpolated stall positions are estimates (can be one stall off) — for scored apartments verify them on a crop and record manual points.
  - plan drafting errors (duplicate stall label, missing number): infer the stall from the numbering sequence of its row and report the assumption to the user.
  - mixed-level record (e.g. `-2 / -1`, `(-2),(-1)`) does not reliably map ids to levels in order: place each id on a level where the same id is NOT already owned by a single-level record; after computing, check that no (level, id) is assigned to two apartments.
  - appendix itself assigns the same stall(s) on the same level to two apartments (verified on the source row, not a parsing error): score each apartment from the appendix value as written, and append to the explanation `| בנספח ג'4 החניות X+Y רשומות גם ל-<building apt>` plus, when the numbering sequence points to a free stall, `, ייתכן שהכוונה ל-<ids> בקומה <level>`. Report it to the user; do not silently reassign.
  - zone note trigger: stall >3 m closer (straight line) to another building's core than to the own core → `| באזור בניין X`.
- **boundary_and_tie_rules:** do not infer zone by parking number alone; locate every stall visually on the parking plan
- **not_applicable_rule:** project-defined for apartments without assigned parking
- **missing_evidence_rule:** leave score blank. At project setup, ask whether a per-apartment assignment appendix (טופס ג'4) exists; without it the criterion cannot be measured — offer to deactivate it or keep it blank until supplied.. At project setup, ask whether a per-apartment assignment appendix (טופס ג'4) exists; without it the criterion cannot be measured — offer to deactivate it or keep it blank until supplied.
- **score_explanation_rule:** always state the approximate walking distance in meters and the parking level. When the stalls are not under/within the apartment's own building block (e.g. under or closer to another building), add a short note naming that building.
- **score_explanation_examples:** `כ-35 מ' הליכה, קומה -1 | מתחת לבניין 6B`; `כ-20 מ' הליכה, קומה -2`; `חניה באזור בניין אחר, כ-75 מ' הליכה`
- **overlap_with_other_criteria:** Storage Proximity uses the same measurement method for storage rooms
- **dependencies:** assigned parking must exist
- **notes:** visual distance measurement is approximate (~±10–15% route tracing)
- **version_history:** v1 = same scoring_rule without measurement_rule; explanation did not require meters or building-block anomaly note. v2 added from project 2181 (שמורת אלמוגים – חיפה).

---

## Criterion: Storage Proximity

- **key:** `storage_proximity`
- **version:** `1`
- **status:** `active`
- **display_name:** `קרבת מחסן`
- **aliases:** Storage proximity
- **purpose:** Measure convenience of reaching the apartment's assigned storage room from its building core.
- **excel_explanation:** `מודד את נוחות הגישה מהמחסן המשויך לדירה אל גרעין הבניין, לפי מרחק הליכה ומפלס המחסן, כולל מקרים שבהם המחסן נמצא באזור של בניין אחר.`
- **scope:** apartment + storage + building
- **applicability:** apartments with an assigned storage room
- **required_sources:** storage assignment table (e.g. ג'4: storage number + level per apartment) and the plan of the storage level (common-area plans)
- **required_observations:** storage location and level, nearest building/core, practical walking route, building-block anomaly
- **cache_fact_fields:** `assigned_storage_id`, `storage_level`, `storage_building_zone`, `storage_walking_distance_m`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** walking distance: <15m=10, 15–30=8, 30–45=6, 45–60=4, 60–90=2, >90=1
- **measurement_rule:** same as Parking Proximity v2 — calibrated scale; walking route from the elevator lobby of the apartment's own building on the storage level to the storage door; round to ~5 m.
- **boundary_and_tie_rules:** do not infer location by storage number alone (numbers may repeat across levels/plots); match number + level from the assignment table
- **case_rules:**
  - storage numbering per building: each building may have its own cluster numbered 1..N on the same level → pick the occurrence nearest the apartment's own core.
  - qualifier in the assignment (`13(B6)`, `(A1) 65`, `19 (B4)`) = that number in the named building's cluster; when it names another building it is also an other-building-zone note (`| באזור בניין B6`).
  - qualified storage number absent from the stated level but present beside the named building on another level → treat as a clerical level error in the assignment table; measure on the plan location and report it to the user (project 2181: 3 cases).
  - split ground levels (`קרקע עליון` / `קרקע תחתון`): measure on the matching sheet from the core point on that sheet; storages missing from the text layer are located manually.
  - number appears several times on the level and the own building has no occurrence: exclude occurrences already claimed by another apartment with the same number + level (e.g. inside that apartment's building cluster), take the remaining one, add the other-building-zone note and report it to the user.
  - zero-padded plan labels (`06`) match the unpadded assignment number (`6`).
- **not_applicable_rule:** apartment without an assigned storage: leave blank
- **missing_evidence_rule:** leave score blank and explain. At project setup, ask whether a per-apartment assignment appendix (טופס ג'4) exists; without it the criterion cannot be measured — offer to deactivate it or keep it blank until supplied.
- **score_explanation_rule:** always state the approximate walking distance in meters and the storage level. When the storage is not within the apartment's own building block (e.g. closer to another building), add a short note naming that building.
- **score_explanation_examples:** `כ-20 מ' הליכה, קרקע עליון`; `כ-50 מ' הליכה, קומה -2 | ליד בניין 5B`
- **overlap_with_other_criteria:** none (separate from Parking Proximity)
- **dependencies:** assigned storage must exist
- **notes:** visual distance measurement is approximate
- **version_history:** v1 added from project 2181 (שמורת אלמוגים – חיפה). v1.1 (same project, C14) added the claimed-duplicate-occurrence and zero-padded-label rules; scoring unchanged.

---

# Version history

- Bank initialized with 7 reusable project-level criteria.
- Floor preference intentionally excluded and delegated to the downstream user-specific ranking application.
- Score explanations standardized to short, simple wording.
- Low-score explanations for Quiet and Location on Floor now require the exact verified cause when score is 0–6.
- Criterion `display_name` and `excel_explanation` are now strict canonical cross-project values and must be reused verbatim from the bank.
- Plugin 1.1.0: merged the project 2181 bank into 1.0.5; the detailed project-2181 `excel_explanation` texts are the canonical values for the current criterion versions.
- Project 2181: Parking Proximity -> v2 (measurement rule, meters + building-block note in explanation); added Storage Proximity v1.
- Project 2181: added case_rules to Parking/Storage Proximity (per-building storage numbering + qualifiers, mixed levels, id ranges, stroke-glyph stall numbers, penalized-wall routing, score on rounded distance). No scoring change.
- Project 2181: added 6↔9 rotated-label rule, interpolation verification for scored apartments, and plan duplicate-label rule to Parking Proximity. No scoring change.
- Project 2181: added mixed-level stall ownership rule (resolve level by uniqueness, verify no stall assigned twice) to Parking Proximity. No scoring change.
- Project 2181: added claimed-duplicate-occurrence and zero-padded-label rules to Storage Proximity. No scoring change.
- Project 2181: added appendix duplicate-assignment rule (score as written + explanation note + probable intended stall). No scoring change.
- Plugin 1.1.0: Parking/Storage Proximity missing_evidence_rule — ask at project setup whether a ג'4 assignment appendix exists. No scoring change.
