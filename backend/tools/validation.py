"""
Schema validation and structured output enforcement.

Provides:
1. JSON schema validation for tool inputs
2. Graceful fallback when model doesn't follow schema
3. Extraction of structured data from free-text responses
"""

import json
import re
from typing import Any, Optional
from jsonschema import validate, ValidationError, Draft7Validator


# Validation schemas for each tool (subset of full schemas for runtime validation)
VALIDATION_SCHEMAS = {
    "analyze_request": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["create_document", "modify_document", "ask_question", "provide_info", "unclear"]
            },
            "document_type": {
                "type": "string",
                "enum": ["NDA", "EMPLOYMENT", "SERVICE", "LEASE", "UNKNOWN"]
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            }
        },
        "required": ["intent"]
    },
    "extract_structured_data": {
        "type": "object",
        "properties": {
            "party_a": {"type": "object"},
            "party_b": {"type": "object"},
            "confidential_info": {"type": "object"},
            "duration": {"type": "object"},
            "governing_law": {"type": "string"}
        }
    },
    "validate_completeness": {
        "type": "object",
        "properties": {
            "is_complete": {"type": "boolean"},
            "ready_to_generate": {"type": "boolean"},
            "missing_required": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["is_complete"]
    },
    "generate_document_section": {
        "type": "object",
        "properties": {
            "section_type": {
                "type": "string",
                "enum": [
                    "header", "parties", "recitals", "definitions",
                    "confidential_info", "obligations", "exclusions",
                    "term_termination", "remedies", "general_provisions", "signatures"
                ]
            },
            "content": {"type": "string"}
        },
        "required": ["section_type", "content"]
    },
    "generate_full_document": {
        "type": "object",
        "properties": {
            "document_type": {
                "type": "string",
                "enum": ["NDA", "EMPLOYMENT", "SERVICE", "LEASE"]
            },
            "title": {"type": "string"},
            "content": {"type": "string"},
            "metadata": {"type": "object"},
            "use_reflection": {"type": "boolean"}
        },
        "required": ["document_type", "title", "content"]
    },
    "apply_revision": {
        "type": "object",
        "properties": {
            "target_section": {"type": "string"},
            "revision_type": {
                "type": "string",
                "enum": ["modify", "delete", "add", "replace"]
            },
            "revised_text": {"type": "string"}
        },
        "required": ["target_section", "revised_text"]
    }
}


class ToolValidationError(Exception):
    """Exception raised when tool input validation fails."""
    def __init__(self, message: str, tool_name: str, field: str = None):
        self.message = message
        self.tool_name = tool_name
        self.field = field
        super().__init__(self.message)


def validate_tool_input(tool_name: str, input_data: dict) -> dict:
    """
    Validate tool input against its schema.

    Args:
        tool_name: Name of the tool
        input_data: Input data to validate

    Returns:
        Validated input data (may be cleaned/coerced)

    Raises:
        ToolValidationError: If validation fails and cannot be recovered
    """
    schema = VALIDATION_SCHEMAS.get(tool_name)
    if not schema:
        # No schema defined, pass through
        return input_data

    try:
        validate(instance=input_data, schema=schema)
        return input_data
    except ValidationError as e:
        # Try to recover with fallback extraction
        recovered = attempt_recovery(tool_name, input_data, e)
        if recovered:
            return recovered
        raise ToolValidationError(
            message=f"Validation failed: {e.message}",
            tool_name=tool_name,
            field=str(e.path) if e.path else None
        )


def attempt_recovery(tool_name: str, input_data: dict, error: ValidationError) -> Optional[dict]:
    """
    Attempt to recover from validation errors by fixing common issues.

    Args:
        tool_name: Name of the tool
        input_data: Original input data
        error: The validation error

    Returns:
        Recovered data or None if recovery not possible
    """
    recovered = input_data.copy()

    # Fix common issues based on tool
    if tool_name == "analyze_request":
        # Default confidence if missing or invalid
        if "confidence" not in recovered or not isinstance(recovered.get("confidence"), (int, float)):
            recovered["confidence"] = 0.5
        # Clamp confidence to valid range
        if isinstance(recovered.get("confidence"), (int, float)):
            recovered["confidence"] = max(0, min(1, recovered["confidence"]))
        # Default intent if missing
        if "intent" not in recovered:
            recovered["intent"] = "unclear"
        # Fix invalid intent
        valid_intents = ["create_document", "modify_document", "ask_question", "provide_info", "unclear"]
        if recovered.get("intent") not in valid_intents:
            recovered["intent"] = "unclear"

    elif tool_name == "validate_completeness":
        # Default is_complete if missing
        if "is_complete" not in recovered:
            recovered["is_complete"] = False
        # Ensure boolean
        if not isinstance(recovered.get("is_complete"), bool):
            recovered["is_complete"] = bool(recovered.get("is_complete"))

    elif tool_name == "generate_document_section":
        # Default content to empty string
        if "content" not in recovered:
            recovered["content"] = ""
        # Default section_type
        if "section_type" not in recovered:
            return None  # Can't recover without section type

    elif tool_name == "apply_revision":
        # Default revision_type
        if "revision_type" not in recovered:
            recovered["revision_type"] = "modify"
        # Default revised_text
        if "revised_text" not in recovered:
            recovered["revised_text"] = ""

    # Validate recovered data
    schema = VALIDATION_SCHEMAS.get(tool_name)
    if schema:
        try:
            validate(instance=recovered, schema=schema)
            return recovered
        except ValidationError:
            return None

    return recovered


def safe_parse_json(json_string: str) -> Optional[dict]:
    """
    Safely parse JSON with fallback strategies.

    Args:
        json_string: JSON string to parse

    Returns:
        Parsed dict or None if parsing fails
    """
    if not json_string:
        return None

    # Try direct parsing
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', json_string)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in text
    json_match = re.search(r'\{[\s\S]*\}', json_string)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def extract_from_freetext(text: str, tool_name: str) -> dict:
    """
    Extract structured data from free-text when JSON parsing fails.

    Args:
        text: Free-text response from LLM
        tool_name: Expected tool name for context

    Returns:
        Best-effort extracted data
    """
    extracted = {}
    text_lower = text.lower()

    if tool_name == "analyze_request":
        # Extract intent
        if any(word in text_lower for word in ["create", "generate", "make", "need"]):
            extracted["intent"] = "create_document"
        elif any(word in text_lower for word in ["change", "modify", "update", "edit"]):
            extracted["intent"] = "modify_document"
        elif "?" in text:
            extracted["intent"] = "ask_question"
        else:
            extracted["intent"] = "unclear"

        # Extract document type
        if "nda" in text_lower or "non-disclosure" in text_lower or "confidential" in text_lower:
            extracted["document_type"] = "NDA"
        elif "employ" in text_lower:
            extracted["document_type"] = "EMPLOYMENT"
        else:
            extracted["document_type"] = "UNKNOWN"

        extracted["confidence"] = 0.3  # Low confidence for free-text extraction

    elif tool_name == "extract_structured_data":
        # Try to extract party names
        name_patterns = [
            r"(?:party\s*a|first\s*party|disclosing)[\s:]+([A-Z][A-Za-z\s]+(?:Inc|LLC|Corp|Ltd)?)",
            r"(?:party\s*b|second\s*party|receiving)[\s:]+([A-Z][A-Za-z\s]+(?:Inc|LLC|Corp|Ltd)?)",
            r"between\s+([A-Z][A-Za-z\s]+(?:Inc|LLC|Corp|Ltd)?)\s+and\s+([A-Z][A-Za-z\s]+(?:Inc|LLC|Corp|Ltd)?)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if "party_a" not in extracted and match.group(1):
                    extracted["party_a"] = {"name": match.group(1).strip()}
                if len(match.groups()) > 1 and "party_b" not in extracted and match.group(2):
                    extracted["party_b"] = {"name": match.group(2).strip()}

        # Try to extract duration
        duration_match = re.search(r"(\d+)\s*(year|month|day)s?", text_lower)
        if duration_match:
            extracted["duration"] = {
                "value": int(duration_match.group(1)),
                "unit": duration_match.group(2) + "s"
            }

        # Try to extract jurisdiction
        states = ["California", "Delaware", "New York", "Texas", "Florida"]
        for state in states:
            if state.lower() in text_lower:
                extracted["governing_law"] = state
                break

    elif tool_name == "validate_completeness":
        # Check for completeness indicators
        if any(word in text_lower for word in ["complete", "ready", "sufficient", "all required"]):
            extracted["is_complete"] = True
            extracted["ready_to_generate"] = True
        else:
            extracted["is_complete"] = False
            extracted["ready_to_generate"] = False

        # Extract missing fields
        missing_match = re.search(r"missing[:\s]+([^.]+)", text_lower)
        if missing_match:
            fields = [f.strip() for f in missing_match.group(1).split(",")]
            extracted["missing_required"] = fields

    elif tool_name == "generate_document_section":
        # The content is likely the whole text
        extracted["content"] = text
        # Try to detect section type
        section_keywords = {
            "header": ["header", "title", "agreement"],
            "parties": ["parties", "party a", "party b"],
            "definitions": ["definitions", "defined terms"],
            "obligations": ["obligations", "shall", "must"],
            "confidential_info": ["confidential information", "protected"],
            "term_termination": ["term", "termination", "duration"],
            "remedies": ["remedies", "breach", "damages"],
        }
        for section, keywords in section_keywords.items():
            if any(kw in text_lower for kw in keywords):
                extracted["section_type"] = section
                break
        if "section_type" not in extracted:
            extracted["section_type"] = "general_provisions"

    elif tool_name == "apply_revision":
        extracted["revised_text"] = text
        extracted["revision_type"] = "modify"
        extracted["target_section"] = "unknown"

    return extracted


def validate_and_parse_tool_call(tool_name: str, arguments: str) -> dict:
    """
    Complete pipeline: parse JSON, validate, fallback to free-text extraction.

    Args:
        tool_name: Name of the tool being called
        arguments: Raw arguments string from LLM

    Returns:
        Validated and parsed arguments dict
    """
    # Step 1: Try to parse as JSON
    parsed = safe_parse_json(arguments)

    # Step 2: If JSON parsing failed, extract from free-text
    if parsed is None:
        parsed = extract_from_freetext(arguments, tool_name)

    # Step 3: Validate and recover if needed
    try:
        validated = validate_tool_input(tool_name, parsed)
        return validated
    except ToolValidationError:
        # Last resort: return minimal valid structure
        return get_minimal_valid_input(tool_name)


def get_minimal_valid_input(tool_name: str) -> dict:
    """
    Get minimal valid input for a tool when all else fails.

    Args:
        tool_name: Name of the tool

    Returns:
        Minimal valid input dict
    """
    minimal_inputs = {
        "analyze_request": {
            "intent": "unclear",
            "document_type": "UNKNOWN",
            "confidence": 0.0
        },
        "extract_structured_data": {},
        "validate_completeness": {
            "is_complete": False,
            "ready_to_generate": False,
            "missing_required": ["unknown"]
        },
        "generate_document_section": {
            "section_type": "general_provisions",
            "content": "[Content generation failed]"
        },
        "apply_revision": {
            "target_section": "unknown",
            "revision_type": "modify",
            "revised_text": ""
        }
    }
    return minimal_inputs.get(tool_name, {})
