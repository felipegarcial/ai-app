"""
Function execution handlers for tool calls.

Each handler processes the tool input and updates conversation state accordingly.
Includes JSON schema validation with graceful fallback.
"""

import logging
from typing import Any
from .validation import validate_tool_input, ToolValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_tool_call(tool_name: str, tool_input: dict, state: Any) -> dict:
    """
    Route tool calls to appropriate handler with validation.

    Args:
        tool_name: Name of the tool being called
        tool_input: Input parameters for the tool
        state: Current conversation state

    Returns:
        Tool execution result
    """
    handlers = {
        "analyze_request": handle_analyze_request,
        "extract_structured_data": handle_extract_structured_data,
        "validate_completeness": handle_validate_completeness,
        "generate_document_section": handle_generate_document_section,
        "generate_full_document": handle_generate_full_document,
        "apply_revision": handle_apply_revision,
    }

    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}", "recoverable": True}

    try:
        # Validate input against schema (with auto-recovery)
        validated_input = validate_tool_input(tool_name, tool_input)
        return handler(validated_input, state)
    except ToolValidationError as e:
        return {
            "error": f"Validation error: {e.message}",
            "tool": tool_name,
            "field": e.field,
            "recoverable": True
        }
    except Exception as e:
        return {
            "error": str(e),
            "tool": tool_name,
            "recoverable": False
        }


def handle_analyze_request(input_data: dict, state: Any) -> dict:
    """
    Handle analyze_request tool call.

    Updates state with detected information and intent.
    Uses confidence score for decision making.
    """
    from features.chat.state import DocumentType

    # Extract confidence score (0-1, default 0.5 if not provided)
    confidence = input_data.get("confidence", 0.5)

    # Confidence thresholds for decision making
    HIGH_CONFIDENCE = 0.8
    LOW_CONFIDENCE = 0.4

    # Log detected document type
    detected_type = input_data.get("document_type", "UNKNOWN")
    logger.info(f"🔍 ANALYZE_REQUEST: Detected document_type = {detected_type}")

    # Update state based on analysis (convert string to Enum)
    if input_data.get("document_type") and input_data["document_type"] != "UNKNOWN":
        try:
            old_type = state.document_type.value
            state.document_type = DocumentType(input_data["document_type"])
            logger.info(f"📄 DOCUMENT_TYPE CHANGED: {old_type} → {state.document_type.value}")
            logger.info(f"📋 NEW REQUIRED FIELDS: {state.missing_fields}")
        except ValueError:
            logger.warning(f"⚠️ Invalid document_type: {input_data['document_type']}")

    # Update missing fields if provided
    if input_data.get("missing_info"):
        state.missing_fields = input_data["missing_info"]

    # Extract any detected info into collected data
    if input_data.get("detected_info"):
        state.update_collected_data(input_data["detected_info"])

    # Determine if clarification is needed based on confidence
    explicit_clarification = input_data.get("clarification_needed", False)
    needs_clarification = explicit_clarification or confidence < LOW_CONFIDENCE

    # Determine confidence level for response guidance
    if confidence >= HIGH_CONFIDENCE:
        confidence_level = "high"
        guidance = "Proceed with collected information"
    elif confidence >= LOW_CONFIDENCE:
        confidence_level = "medium"
        guidance = "Consider asking for confirmation"
    else:
        confidence_level = "low"
        guidance = "Request clarification before proceeding"

    return {
        "success": True,
        "intent": input_data.get("intent"),
        "document_type": state.document_type.value,
        "needs_clarification": needs_clarification,
        "confidence": confidence,
        "confidence_level": confidence_level,
        "guidance": guidance
    }


def handle_extract_structured_data(input_data: dict, state: Any) -> dict:
    """
    Handle extract_structured_data tool call.

    Extracts typed data from conversation and updates state.
    """
    extracted = {}

    # Extract party information
    if input_data.get("party_a"):
        party_a = input_data["party_a"]
        if party_a.get("name"):
            extracted["party_a_name"] = party_a["name"]
        if party_a.get("type"):
            extracted["party_a_type"] = party_a["type"]

    if input_data.get("party_b"):
        party_b = input_data["party_b"]
        if party_b.get("name"):
            extracted["party_b_name"] = party_b["name"]
        if party_b.get("type"):
            extracted["party_b_type"] = party_b["type"]

    # Extract confidential info
    if input_data.get("confidential_info"):
        conf_info = input_data["confidential_info"]
        if conf_info.get("description"):
            extracted["confidential_info_type"] = conf_info["description"]

    # Extract duration
    if input_data.get("duration"):
        duration = input_data["duration"]
        extracted["duration"] = f"{duration.get('value', '')} {duration.get('unit', '')}"

    # Extract governing law
    if input_data.get("governing_law"):
        extracted["governing_law"] = input_data["governing_law"]

    # Update state with extracted data
    state.update_collected_data(extracted)

    return {
        "success": True,
        "extracted_fields": list(extracted.keys()),
        "remaining_fields": state.missing_fields
    }


def handle_validate_completeness(input_data: dict, state: Any) -> dict:
    """
    Handle validate_completeness tool call.

    Checks if we have enough information to generate the document.
    """
    is_complete = input_data.get("is_complete", False)
    ready = input_data.get("ready_to_generate", False)

    # If complete and ready, advance to clarification or generation phase
    if is_complete and ready:
        from features.chat.state import Phase
        if state.phase == Phase.INTAKE:
            state.phase = Phase.CLARIFICATION
        elif state.phase == Phase.CLARIFICATION:
            state.phase = Phase.GENERATION

    return {
        "success": True,
        "is_complete": is_complete,
        "ready_to_generate": ready,
        "current_phase": state.phase.value,
        "missing_required": input_data.get("missing_required", []),
        "recommendation": input_data.get("recommendation", "")
    }


def handle_generate_document_section(input_data: dict, state: Any) -> dict:
    """
    Handle generate_document_section tool call.

    Generates a section and appends to current document.
    """
    section_type = input_data.get("section_type", "")
    content = input_data.get("content", "")
    section_number = input_data.get("section_number", "")

    # Format section
    if section_number:
        formatted_section = f"\n{section_number}. {section_type.upper()}\n\n{content}\n"
    else:
        formatted_section = f"\n{section_type.upper()}\n\n{content}\n"

    # Append to current document
    if state.current_document:
        state.current_document += formatted_section
    else:
        state.current_document = formatted_section

    return {
        "success": True,
        "section_type": section_type,
        "section_added": True
    }


def handle_generate_full_document(input_data: dict, state: Any) -> dict:
    """
    Handle generate_full_document tool call.

    Stores the complete document in state for preview and export.
    Optionally applies reflection pattern to critical sections.
    """
    from features.chat.state import Phase
    from prompts.patterns.reflection import (
        get_section_config,
        CRITICAL_SECTIONS_BY_DOCTYPE,
        ReflectionAgent
    )

    document_type = input_data.get("document_type", "NDA")
    title = input_data.get("title", "Legal Document")
    content = input_data.get("content", "")
    metadata = input_data.get("metadata", {})
    use_reflection = input_data.get("use_reflection", False)

    # Log reflection status
    if use_reflection:
        logger.info(f"🔄 REFLECTION MODE: ENABLED for {document_type}")
    else:
        logger.info(f"⚡ REFLECTION MODE: DISABLED (fast generation) for {document_type}")

    # If reflection is requested, apply it to critical sections
    if use_reflection and content:
        critical_sections = CRITICAL_SECTIONS_BY_DOCTYPE.get(
            document_type, {}
        ).get("critical", [])

        if critical_sections:
            agent = ReflectionAgent()
            # Apply reflection to improve the document
            result = agent.run(
                user_msg=f"Review and improve this {document_type} document, focusing on these critical sections: {', '.join(critical_sections)}.\n\nDocument:\n{content}",
                generation_system_prompt=f"You are improving a {document_type} legal document. Focus on legal accuracy, clarity, and completeness.",
                n_steps=2,
                verbose=False
            )
            content = result.get("content", content)

    # Store the full document
    state.current_document = content
    state.document_metadata = {
        "title": title,
        "document_type": document_type,
        "used_reflection": use_reflection,
        **metadata
    }

    # Move to revision phase
    state.phase = Phase.REVISION

    # Get critical sections info for response
    critical_info = CRITICAL_SECTIONS_BY_DOCTYPE.get(document_type, {})

    return {
        "success": True,
        "document_type": document_type,
        "title": title,
        "document_generated": True,
        "used_reflection": use_reflection,
        "critical_sections": critical_info.get("critical", []),
        "message": "Document generated successfully. User can now preview, export, or request revisions."
    }


def handle_apply_revision(input_data: dict, state: Any) -> dict:
    """
    Handle apply_revision tool call.

    Modifies the existing document based on revision request.
    """
    revision_type = input_data.get("revision_type", "modify")
    target_section = input_data.get("target_section", "")
    original_text = input_data.get("original_text", "")
    revised_text = input_data.get("revised_text", "")

    if not state.current_document:
        return {
            "success": False,
            "error": "No document to revise"
        }

    # Apply revision
    if revision_type == "replace" and original_text:
        state.current_document = state.current_document.replace(original_text, revised_text)
    elif revision_type == "add":
        state.current_document += f"\n{revised_text}"
    elif revision_type == "modify" and original_text:
        state.current_document = state.current_document.replace(original_text, revised_text)

    # Set phase to revision
    from features.chat.state import Phase
    state.phase = Phase.REVISION

    return {
        "success": True,
        "revision_type": revision_type,
        "target_section": target_section,
        "affected_sections": input_data.get("affected_sections", [])
    }
