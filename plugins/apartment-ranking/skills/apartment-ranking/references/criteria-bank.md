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
- Keep `excel_explanation` and generated `הסבר הציון` text short and simple. `excel_explanation` should be one short sentence; score explanations should be a short phrase or one short sentence with only the decisive evidence.
- `display_name` and `excel_explanation` are **canonical cross-project metadata**. For any project using an existing criterion version, copy both values verbatim from this bank. Do not paraphrase, translate, shorten, expand, or otherwise adapt them to the project.
- Once a new criterion is confirmed and added here, its `display_name` and `excel_explanation` become the canonical values for all future projects using that version.
- If the user explicitly requests a change to a criterion name or generic description, update/version this bank entry first. Do not create a silent project-only variant by default.

---

## Criterion: Quiet

- **key:** `quiet`
- **version:** `1`
- **status:** `active`
- **display_name:** `שקט`
- **aliases:** Quiet; רעש
- **purpose:** Measure expected exposure to identifiable external and internal project noise sources.
- **excel_explanation:** `מודד חשיפה לרעש חיצוני ופנימי סביב הדירה.`
- **scope:** apartment + building + plot/site
- **applicability:** normally all apartments
- **required_sources:** site/development plan, typical floor plan; other sources as needed
- **required_observations:** road/rail/commercial/playground/garage-ramp exposure; elevator/refuse/service adjacency; floor-height noise attenuation if used
- **cache_fact_fields:** `road_exposure`, `rail_exposure`, `commercial_exposure`, `playground_exposure`, `garage_ramp_exposure`, `elevator_adjacency_room`, `refuse_or_service_adjacency`, `floor`
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
- **boundary_and_tie_rules:** apply only verified factors; cap final score to range
- **not_applicable_rule:** normally applicable
- **missing_evidence_rule:** leave score blank and explain uncertainty
- **score_explanation_rule:** keep it short. If score is 0–6, state the exact verified noise cause(s) that lowered the score; never use a generic label like `רועש`. For scores 7–10, a minimal positive/neutral explanation is enough.
- **score_explanation_examples:** low: `פונה לכביש ראשי`; `ליד רמפת חניה`; `חדר שינה צמוד לפיר מעלית`; combined only when needed: `כביש ראשי + קומה נמוכה`. high: `ללא מקור רעש משמעותי`
- **overlap_with_other_criteria:** elevator/core adjacency may also affect Location on Floor; keep distinctions explicit
- **dependencies:** none
- **notes:** floor here is only a noise attenuation factor, not personal floor preference

---

## Criterion: Location on Floor

- **key:** `location_on_floor`
- **version:** `1`
- **status:** `active`
- **display_name:** `מיקום בקומה`
- **aliases:** Location on floor
- **purpose:** Measure apartment position relative to building core and shared circulation/service elements.
- **excel_explanation:** `מודד את מיקום הדירה ביחס למעליות, מדרגות ומעברים משותפים.`
- **scope:** apartment + floor
- **applicability:** normally all apartments
- **required_sources:** typical floor plan, apartment plan when needed
- **required_observations:** corner/interior position; elevator contact; refuse/service-riser contact; stair/corridor adjacency; isolation from core
- **cache_fact_fields:** `position_on_floor`, `core_adjacency`, `elevator_adjacency_room`, `refuse_or_service_adjacency`, `stair_adjacency`, `corridor_adjacency`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** fallback baseline corner=8, interior=6; overrides: living room on elevator=4, refuse chute=4, service riser=5, bedroom on elevator=6, stairwell only=7; well-isolated may receive +1 up to 10
- **boundary_and_tie_rules:** actual room/core geometry takes precedence over generic corner/interior classification
- **not_applicable_rule:** normally applicable
- **missing_evidence_rule:** leave score blank
- **score_explanation_rule:** keep it short. If score is 0–6, state the exact verified floor-position cause that lowered the score; never use a generic label like `מיקום פחות טוב`. For scores 7–10, a minimal positive/neutral explanation is enough.
- **score_explanation_examples:** low: `סלון צמוד לפיר מעלית`; `צמוד לחדר אשפה`; `צמוד למעבר משותף`. high: `דירת פינה, רחוקה מהגרעין`
- **overlap_with_other_criteria:** some core adjacency can also affect Quiet
- **dependencies:** none
- **notes:** none

---

## Criterion: Direction Quality

- **key:** `direction_quality`
- **version:** `1`
- **status:** `active`
- **display_name:** `איכות כיוון`
- **aliases:** Direction quality
- **purpose:** Measure shared project-level direction quality using a declared climate/orientation convention.
- **excel_explanation:** `מודד את איכות כיווני הדירה לפי הכיוונים שהוגדרו לפרויקט.`
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
- **excel_explanation:** `מודד את מספר החזיתות החיצוניות של הדירה.`
- **scope:** apartment
- **applicability:** normally all apartments
- **required_sources:** typical floor plan / apartment plan
- **required_observations:** every apartment boundary wall and whether it is a true exterior facade with relevant openings
- **cache_fact_fields:** `exterior_facade_count`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** fallback: 4 facades=10, 3=9, 2=7, 1=5, 0=3
- **boundary_and_tie_rules:** shared/core/corridor walls do not count
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
- **excel_explanation:** `מודד את רמת הפרטיות מול שטחים משותפים וציבוריים.`
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
- **excel_explanation:** `מודד כמה דירות חולקות את אותה קומה.`
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
- **version:** `1`
- **status:** `active`
- **display_name:** `קרבת חניה`
- **aliases:** Parking proximity
- **purpose:** Measure convenience of reaching assigned parking from the apartment's building/core.
- **excel_explanation:** `מודד את נוחות ומרחק הגישה מהחניה לבניין.`
- **scope:** apartment + parking + building
- **applicability:** apartments with assigned parking
- **required_sources:** parking assignment source and parking plans
- **required_observations:** assigned-space location, nearest building/core, practical walking route, level, anomaly
- **cache_fact_fields:** `assigned_parking_id`, `parking_building_zone`, `parking_walking_distance_m`, `parking_level`
- **score_range:** 0–10
- **allow_decimal_scores:** false
- **scoring_rule:** distance fallback: <30m=9, 30–45=7, 45–60=6, 60–75=4, 75–90=3, 90–105=2, >105=1; normal close/non-anomalous assignment may be 10 when project convention supports it
- **boundary_and_tie_rules:** do not infer zone by parking number alone
- **not_applicable_rule:** project-defined for apartments without assigned parking
- **missing_evidence_rule:** leave score blank
- **score_explanation_rule:** state anomaly and/or approximate distance/level
- **score_explanation_examples:** `חניה באזור בניין אחר, כ-75 מ' הליכה`
- **overlap_with_other_criteria:** none
- **dependencies:** assigned parking must exist
- **notes:** visual distance measurement is approximate

---

# Version history

- Bank initialized with 7 reusable project-level criteria.
- Floor preference intentionally excluded and delegated to the downstream user-specific ranking application.
- Excel criterion and score explanations standardized to short, simple wording.
- Low-score explanations for Quiet and Location on Floor now require the exact verified cause when score is 0–6.
- Criterion `display_name` and `excel_explanation` are now strict canonical cross-project values and must be reused verbatim from the bank.
