"""
Function calling schemas for the legal document assistant.

Core functions:
1. analyze_request - Parse user intent, identify document type, detect missing info
2. extract_structured_data - Pull typed, validated data from conversation
3. validate_completeness - Check if sufficient info exists to generate document
4. generate_document_section - Generate specific sections with legal language
5. apply_revision - Modify existing document based on user feedback
"""

TOOLS = [
    {
        "name": "analyze_request",
        "description": "Analyze the user's request to determine intent, document type, and identify any missing information needed to proceed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["create_document", "modify_document", "ask_question", "provide_info", "unclear"],
                    "description": "The detected intent of the user's message"
                },
                "document_type": {
                    "type": "string",
                    "enum": ["NDA", "EMPLOYMENT", "SERVICE", "LEASE", "UNKNOWN"],
                    "description": "The type of legal document being requested. Detect from user's message: 'employment contract'=EMPLOYMENT, 'NDA/confidentiality'=NDA, 'service agreement'=SERVICE, 'lease/rental'=LEASE"
                },
                "detected_info": {
                    "type": "object",
                    "description": "Key-value pairs of information detected in the request",
                    "additionalProperties": {"type": "string"}
                },
                "missing_info": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of required information still needed"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence score for this analysis (0-1)"
                },
                "clarification_needed": {
                    "type": "boolean",
                    "description": "Whether clarification should be requested from user"
                }
            },
            "required": ["intent", "document_type", "confidence"]
        }
    },
    {
        "name": "extract_structured_data",
        "description": "Extract and validate structured data from the conversation into a typed schema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "party_a": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "type": {"type": "string", "enum": ["individual", "company"]},
                        "address": {"type": "string"},
                        "role": {"type": "string", "enum": ["disclosing", "receiving", "mutual"]}
                    },
                    "required": ["name"]
                },
                "party_b": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "type": {"type": "string", "enum": ["individual", "company"]},
                        "address": {"type": "string"},
                        "role": {"type": "string", "enum": ["disclosing", "receiving", "mutual"]}
                    },
                    "required": ["name"]
                },
                "confidential_info": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "categories": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "duration": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "integer", "minimum": 1},
                        "unit": {"type": "string", "enum": ["days", "months", "years"]}
                    }
                },
                "governing_law": {
                    "type": "string",
                    "description": "Jurisdiction/state for governing law"
                },
                "effective_date": {
                    "type": "string",
                    "format": "date",
                    "description": "When the agreement takes effect"
                }
            }
        }
    },
    {
        "name": "validate_completeness",
        "description": "Check if all required information has been collected to generate the document.",
        "input_schema": {
            "type": "object",
            "properties": {
                "is_complete": {
                    "type": "boolean",
                    "description": "Whether all required fields are present"
                },
                "missing_required": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of missing required fields"
                },
                "missing_optional": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of missing optional fields that could enhance the document"
                },
                "validation_errors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "error": {"type": "string"}
                        }
                    },
                    "description": "Any validation errors in the collected data"
                },
                "ready_to_generate": {
                    "type": "boolean",
                    "description": "Whether we can proceed to document generation"
                },
                "recommendation": {
                    "type": "string",
                    "description": "Suggested next action"
                }
            },
            "required": ["is_complete", "ready_to_generate"]
        }
    },
    {
        "name": "generate_document_section",
        "description": "Generate a specific section of the legal document with appropriate legal language.",
        "input_schema": {
            "type": "object",
            "properties": {
                "section_type": {
                    "type": "string",
                    "enum": [
                        "header",
                        "parties",
                        "recitals",
                        "definitions",
                        "confidential_info",
                        "obligations",
                        "exclusions",
                        "term_termination",
                        "remedies",
                        "general_provisions",
                        "signatures"
                    ],
                    "description": "The type of section to generate"
                },
                "content": {
                    "type": "string",
                    "description": "The generated section content"
                },
                "section_number": {
                    "type": "string",
                    "description": "Section number for the document"
                },
                "notes": {
                    "type": "string",
                    "description": "Any notes or explanations about this section"
                }
            },
            "required": ["section_type", "content"]
        }
    },
    {
        "name": "generate_full_document",
        "description": "Generate the complete legal document. Use this when you have all required information and are ready to create the full document. Set use_reflection=true for higher quality on critical sections.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_type": {
                    "type": "string",
                    "enum": ["NDA", "EMPLOYMENT", "SERVICE", "LEASE"],
                    "description": "The type of document being generated"
                },
                "title": {
                    "type": "string",
                    "description": "Document title (e.g., 'Non-Disclosure Agreement')"
                },
                "content": {
                    "type": "string",
                    "description": "The complete document content with all sections"
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "party_a": {"type": "string"},
                        "party_b": {"type": "string"},
                        "effective_date": {"type": "string"},
                        "governing_law": {"type": "string"}
                    },
                    "description": "Document metadata for export"
                },
                "use_reflection": {
                    "type": "boolean",
                    "description": "If true, applies reflection pattern to review and improve critical sections. Slower but higher quality.",
                    "default": False
                }
            },
            "required": ["document_type", "title", "content"]
        }
    },
    {
        "name": "apply_revision",
        "description": "Modify an existing document section based on user feedback.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target_section": {
                    "type": "string",
                    "description": "The section being modified"
                },
                "revision_type": {
                    "type": "string",
                    "enum": ["modify", "delete", "add", "replace"],
                    "description": "Type of revision being applied"
                },
                "original_text": {
                    "type": "string",
                    "description": "The original text being changed"
                },
                "revised_text": {
                    "type": "string",
                    "description": "The new text after revision"
                },
                "reason": {
                    "type": "string",
                    "description": "Explanation of why this change was made"
                },
                "affected_sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Other sections that may need updates due to this change"
                }
            },
            "required": ["target_section", "revision_type", "revised_text"]
        }
    }
]
