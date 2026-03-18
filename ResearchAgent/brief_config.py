"""
Brief configuration derived from configuration_schema.json.

Loads the schema at import time and builds CONCEPT_TYPE_CONFIG — a dict
keyed by each of the 6 supported concept types with their common fields,
type-specific fields, purpose, and minimum-generation rules.
"""

import json
import os

_SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "ARCHandDESIGN", "configuration_schema.json"
)

with open(_SCHEMA_PATH, "r", encoding="utf-8") as _f:
    CONFIGURATION_SCHEMA = json.load(_f)

SUPPORTED_CONCEPT_TYPES: list[str] = CONFIGURATION_SCHEMA["supported_concept_types"]

COMMON_FIELDS: list[dict] = CONFIGURATION_SCHEMA["common_fields"]


def _build_concept_type_config() -> dict:
    """Build a lookup dict from the schema for each concept type."""
    config = {}
    type_fields = CONFIGURATION_SCHEMA.get("concept_type_fields", {})
    for ctype in SUPPORTED_CONCEPT_TYPES:
        type_data = type_fields.get(ctype, {})
        config[ctype] = {
            "purpose": type_data.get("purpose", ""),
            "minimum_generation_rule": type_data.get("minimum_generation_rule", ""),
            "common_fields": COMMON_FIELDS,
            "type_specific_fields": type_data.get("fields", []),
        }
    return config


CONCEPT_TYPE_CONFIG = _build_concept_type_config()

# Human-readable labels for greeting/display
CONCEPT_TYPE_LABELS = {
    "product_concept": "Product Concepts",
    "feature_innovation_concept": "Feature & Innovation Concepts",
    "claim_concept": "Claims",
    "visual_image_pack_concept": "Visual & Pack Concepts",
    "ad_communication_concept": "Ad & Communication Concepts",
    "value_proposition_naming_concept": "Value Propositions & Naming",
}
