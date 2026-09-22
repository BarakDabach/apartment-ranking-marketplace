# Architectural Cache Contract

## Why this cache exists

The cache minimizes repeated model exposure to large architectural sources while preserving evidence traceability.

The cache is **not** a replacement for the original drawings. It is an index + derived evidence layer.

## `manifest.json`

Top-level fields:

- `schema_version`
- `generated_at_utc`
- `sources[]`

Each source contains:

- `source_id`
- `original_path`
- `filename`
- `sha256`
- `media_type`
- `size_bytes`
- `page_count`
- `pages[]`

Each page contains:

- `page_number` (1-based)
- `width_points` / `height_points` when available
- `native_text_chars`
- `markdown_path`
- `preview_path`
- `page_type` (nullable)
- `plot` (nullable)
- `building` (nullable)
- `floor` (nullable)
- `apartment_refs[]`
- `north_or_compass_visible` (nullable)
- `relevant_for[]`
- `review_status`: `unreviewed | reviewed | ambiguous`

## `derived/facts.json`

Use atomic facts. This supports recalculating criteria without re-reading sources.

Example:

```json
{
  "schema_version": 1,
  "facts": [
    {
      "fact_id": "apt-A3-facades",
      "entity_type": "apartment_type",
      "entity_id": "A3",
      "field": "exterior_facade_count",
      "value": 2,
      "unit": null,
      "confidence": "high",
      "evidence": [
        {
          "source_id": "plans-8ab21f90",
          "page_number": 17,
          "crop_path": "crops/plans-8ab21f90/p0017-apt-A3.webp",
          "note": "Two walls with exterior openings face outside air."
        }
      ],
      "depends_on_source_hashes": {
        "plans-8ab21f90": "8ab21f90..."
      }
    }
  ]
}
```

Recommended `entity_type` values:

- `project`
- `plot`
- `building`
- `floor`
- `apartment`
- `apartment_type`
- `parking`
- `storage`
- `site_edge`

Recommended reusable fields include:

- `primary_directions`
- `balcony_direction`
- `exterior_facade_count`
- `cross_ventilation_possible`
- `units_on_floor`
- `core_adjacency`
- `elevator_adjacency_room`
- `refuse_or_service_adjacency`
- `assigned_parking_id`
- `parking_level`
- `parking_walking_distance_m`
- `parking_building_zone`
- `adjacent_external_use`
- `road_exposure`
- `garden_or_private_yard`

The list is extensible. New criteria should prefer adding missing atomic fields rather than adding opaque criterion-specific results.

## Fact confidence

- `high`: directly visible/declared and unambiguous in authoritative source.
- `medium`: supported but requires interpretation/approximate measurement.
- `low`: provisional; downstream scoring should generally remain blank until verified if the criterion needs certainty.

## Invalidation

A fact is stale if any source hash listed in `depends_on_source_hashes` no longer matches the current manifest.
