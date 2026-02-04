from .reflection import (
    ReflectionAgent,
    generate_section,
    generate_full_document,
    SECTION_CONFIG
)

from .chain_of_thought import (
    get_cot_prompt,
    build_cot_prompt,
    COT_LEGAL_DOCUMENT,
    COT_REVISION,
    COT_EXTRACTION,
    COT_PROMPTS
)

__all__ = [
    # Reflection Pattern
    "ReflectionAgent",
    "generate_section",
    "generate_full_document",
    "SECTION_CONFIG",
    # Chain-of-Thought Pattern
    "get_cot_prompt",
    "build_cot_prompt",
    "COT_LEGAL_DOCUMENT",
    "COT_REVISION",
    "COT_EXTRACTION",
    "COT_PROMPTS",
]
