import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from prompts.patterns.chain_of_thought import get_cot_prompt

# Setup Jinja2 environment
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(default=False),  # No HTML escaping for prompts
    trim_blocks=True,
    lstrip_blocks=True
)

# Map phases to their CoT prompt types
PHASE_COT_MAP = {
    "generation": "legal_document",
    "revision": "revision",
}


def get_template(name: str):
    """Load a Jinja2 template by name"""
    return env.get_template(name)


def compose_prompt(phase: str, context: dict) -> str:
    """
    Compose a full prompt by combining all layers.

    Layers:
    1. Base (meta-system) - Overall behavior and safety
    2. Legal domain - Legal knowledge and terminology
    3. Phase-specific - Current task instructions
    4. Patterns - Chain-of-Thought, etc. (injected based on phase)

    Args:
        phase: Current conversation phase (intake, clarification, generation, revision)
        context: Dynamic context data

    Returns:
        Fully composed prompt string
    """
    # Load templates
    base_template = get_template("base.j2")
    legal_template = get_template("legal.j2")
    phase_template = get_template(f"phases/{phase}.j2")

    # Inject Chain-of-Thought pattern if applicable for this phase
    enriched_context = {**context}
    if phase in PHASE_COT_MAP:
        enriched_context["cot_prompt"] = get_cot_prompt(PHASE_COT_MAP[phase])

    # Render each layer
    base_prompt = base_template.render()
    legal_prompt = legal_template.render(document_type=context.get("document_type", "NDA"))
    phase_prompt = phase_template.render(**enriched_context)

    # Compose final prompt
    return f"""{base_prompt}

{legal_prompt}

{phase_prompt}"""
