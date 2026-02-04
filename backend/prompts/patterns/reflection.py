"""
Reflection Pattern Implementation

This pattern implements a generate-reflect loop where:
1. Generator creates content based on user request
2. Reflector critiques the content
3. Generator revises based on critique
4. Loop until Reflector approves (<OK>) or max steps reached

This implements multiple Advanced Prompt Techniques:
- Self-Consistency Checking
- Output Validation Prompts
"""

from typing import Generator
from openai import OpenAI
from config import Config
import llm


# Selective Reflection Configuration by Document Type
# Critical sections vary depending on the type of legal document

CRITICAL_SECTIONS_BY_DOCTYPE = {
    "NDA": {
        "critical": ["confidential_info", "obligations", "exclusions", "remedies"],
        "max_steps": {"confidential_info": 3, "obligations": 3, "exclusions": 2, "remedies": 2}
    },
    "EMPLOYMENT": {
        "critical": ["compensation", "termination", "non_compete", "intellectual_property"],
        "max_steps": {"compensation": 2, "termination": 3, "non_compete": 3, "intellectual_property": 2}
    },
    "SERVICE": {
        "critical": ["scope_of_work", "payment_terms", "liability", "termination"],
        "max_steps": {"scope_of_work": 3, "payment_terms": 2, "liability": 3, "termination": 2}
    },
    "LEASE": {
        "critical": ["rent_terms", "maintenance", "termination", "security_deposit"],
        "max_steps": {"rent_terms": 2, "maintenance": 2, "termination": 3, "security_deposit": 2}
    }
}

# Default fallback for unknown document types
DEFAULT_CRITICAL_SECTIONS = ["obligations", "liability", "termination"]
DEFAULT_MAX_STEPS = 2


def get_section_config(section_type: str, document_type: str = "NDA") -> dict:
    """
    Get configuration for a section based on document type.

    Args:
        section_type: The section being generated
        document_type: Type of document (NDA, EMPLOYMENT, etc.)

    Returns:
        dict with 'use_reflection' and 'max_steps'
    """
    doc_config = CRITICAL_SECTIONS_BY_DOCTYPE.get(document_type, {})
    critical_sections = doc_config.get("critical", DEFAULT_CRITICAL_SECTIONS)
    max_steps_config = doc_config.get("max_steps", {})

    if section_type in critical_sections:
        return {
            "use_reflection": True,
            "max_steps": max_steps_config.get(section_type, DEFAULT_MAX_STEPS)
        }
    else:
        return {
            "use_reflection": False,
            "max_steps": 1
        }


# Legacy config for backwards compatibility
SECTION_CONFIG = {
    "header": {"use_reflection": False},
    "parties": {"use_reflection": False},
    "definitions": {"use_reflection": False},
    "term_termination": {"use_reflection": False},
    "general_provisions": {"use_reflection": False},
    "signatures": {"use_reflection": False},
    "confidential_info": {"use_reflection": True, "max_steps": 3},
    "obligations": {"use_reflection": True, "max_steps": 3},
    "exclusions": {"use_reflection": True, "max_steps": 2},
    "remedies": {"use_reflection": True, "max_steps": 2},
}


GENERATION_SYSTEM_PROMPT = """
Your task is to generate the best legal document content possible for the user's request.
If the user provides critique, respond with a revised version of your previous attempt.
You must always output the revised content in full.

Guidelines:
- Use proper legal language and formatting
- Be precise and unambiguous
- Include all required information
- Follow standard legal document structure
"""

REFLECTION_SYSTEM_PROMPT = """
You are a legal document reviewer. Your task is to critique and provide recommendations
for improving the generated legal document content.

Review for:
1. Legal accuracy and appropriate terminology
2. Completeness - all required sections present
3. Clarity - no ambiguous language
4. Consistency - no contradictions
5. Formatting - proper legal document structure

If there are issues to fix, output a numbered list of specific critiques and recommendations.
If the content is acceptable and ready for use, output exactly: <OK>
"""


class FixedFirstChatHistory(list):
    """
    A chat history that maintains a fixed first message (system prompt)
    and limits total length to manage context window.
    """

    def __init__(self, initial_messages: list, total_length: int = 5):
        super().__init__(initial_messages)
        self.total_length = total_length
        self.first_message = initial_messages[0] if initial_messages else None

    def append(self, message: dict):
        super().append(message)
        # Keep first message + most recent messages
        while len(self) > self.total_length:
            if len(self) > 1:
                self.pop(1)  # Remove second message, keep first


class ReflectionAgent:
    """
    Implements the Reflection Pattern for iterative content improvement.

    The agent alternates between generating content and reflecting on it,
    using the reflection feedback to improve the generation until the
    reflector approves or max steps are reached.
    """

    def __init__(self, model: str = None):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = model or Config.OPENAI_MODEL

    def _completion(self, messages: list) -> str:
        """Request a completion from OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=Config.MAX_TOKENS,
            messages=list(messages)
        )
        return response.choices[0].message.content or ""

    def generate(self, generation_history: list, verbose: bool = False) -> str:
        """Generate content based on the conversation history."""
        output = self._completion(generation_history)
        if verbose:
            print(f"\n{'='*50}\nGENERATION:\n{'='*50}\n{output}\n")
        return output

    def reflect(self, reflection_history: list, verbose: bool = False) -> str:
        """Reflect on and critique the generated content."""
        output = self._completion(reflection_history)
        if verbose:
            print(f"\n{'='*50}\nREFLECTION:\n{'='*50}\n{output}\n")
        return output

    def run(
        self,
        user_msg: str,
        generation_system_prompt: str = "",
        reflection_system_prompt: str = "",
        n_steps: int = 5,
        verbose: bool = False
    ) -> dict:
        """
        Run the reflection loop.

        Args:
            user_msg: The user's request/input
            generation_system_prompt: Additional context for generation
            reflection_system_prompt: Additional context for reflection
            n_steps: Maximum generate-reflect cycles
            verbose: Print intermediate outputs

        Returns:
            dict with 'content' (final generation) and 'iterations' (number of cycles)
        """
        # Combine custom prompts with base prompts
        gen_prompt = generation_system_prompt + "\n\n" + GENERATION_SYSTEM_PROMPT
        ref_prompt = reflection_system_prompt + "\n\n" + REFLECTION_SYSTEM_PROMPT

        # Initialize histories with fixed first message (system prompt)
        generation_history = FixedFirstChatHistory(
            [
                {"role": "system", "content": gen_prompt},
                {"role": "user", "content": user_msg}
            ],
            total_length=5
        )

        reflection_history = FixedFirstChatHistory(
            [{"role": "system", "content": ref_prompt}],
            total_length=5
        )

        generation = ""

        for step in range(n_steps):
            if verbose:
                print(f"\n{'#'*50}\nSTEP {step + 1}/{n_steps}\n{'#'*50}")

            # Generate content
            generation = self.generate(generation_history, verbose=verbose)
            generation_history.append({"role": "assistant", "content": generation})
            reflection_history.append({"role": "user", "content": generation})

            # Reflect and critique
            critique = self.reflect(reflection_history, verbose=verbose)

            # Check if approved
            if "<OK>" in critique:
                if verbose:
                    print(f"\n✅ Content approved after {step + 1} iteration(s)\n")
                return {
                    "content": generation,
                    "iterations": step + 1,
                    "approved": True
                }

            # Add critique to histories for next iteration
            generation_history.append({"role": "user", "content": critique})
            reflection_history.append({"role": "assistant", "content": critique})

        if verbose:
            print(f"\n⚠️ Max iterations ({n_steps}) reached\n")

        return {
            "content": generation,
            "iterations": n_steps,
            "approved": False
        }

    def run_stream(
        self,
        user_msg: str,
        generation_system_prompt: str = "",
        reflection_system_prompt: str = "",
        n_steps: int = 5
    ) -> Generator[dict, None, None]:
        """
        Run the reflection loop with streaming updates.

        Yields:
            dict with 'type' (generation|reflection|complete) and 'content'
        """
        gen_prompt = generation_system_prompt + "\n\n" + GENERATION_SYSTEM_PROMPT
        ref_prompt = reflection_system_prompt + "\n\n" + REFLECTION_SYSTEM_PROMPT

        generation_history = FixedFirstChatHistory(
            [
                {"role": "system", "content": gen_prompt},
                {"role": "user", "content": user_msg}
            ],
            total_length=5
        )

        reflection_history = FixedFirstChatHistory(
            [{"role": "system", "content": ref_prompt}],
            total_length=5
        )

        generation = ""

        for step in range(n_steps):
            yield {"type": "step", "step": step + 1, "max_steps": n_steps}

            # Generate
            generation = self.generate(generation_history)
            yield {"type": "generation", "content": generation}

            generation_history.append({"role": "assistant", "content": generation})
            reflection_history.append({"role": "user", "content": generation})

            # Reflect
            critique = self.reflect(reflection_history)
            yield {"type": "reflection", "content": critique}

            if "<OK>" in critique:
                yield {
                    "type": "complete",
                    "content": generation,
                    "iterations": step + 1,
                    "approved": True
                }
                return

            generation_history.append({"role": "user", "content": critique})
            reflection_history.append({"role": "assistant", "content": critique})

        yield {
            "type": "complete",
            "content": generation,
            "iterations": n_steps,
            "approved": False
        }


def generate_section(section_type: str, context: dict, verbose: bool = False) -> dict:
    """
    Generate a document section with or without reflection based on document type.

    Args:
        section_type: Type of section (header, parties, obligations, etc.)
        context: Data for generating the section (parties, terms, etc.)
        verbose: Print progress

    Returns:
        dict with 'content', 'method', 'iterations', 'section_type'
    """
    # Get config based on document type (dynamic)
    document_type = context.get("document_type", "NDA")
    config = get_section_config(section_type, document_type)

    # Build the generation prompt
    section_prompt = f"""
Generate the {section_type.upper().replace('_', ' ')} section for a legal document.

Document Type: {context.get('document_type', 'NDA')}

Data to include:
- Party A: {context.get('party_a_name', 'N/A')}
- Party B: {context.get('party_b_name', 'N/A')}
- Confidential Information: {context.get('confidential_info_type', 'N/A')}
- Duration: {context.get('duration', 'N/A')}
- Governing Law: {context.get('governing_law', 'N/A')}

Generate only the {section_type} section, properly formatted with legal language.
"""

    if config["use_reflection"]:
        if verbose:
            print(f"📄 {section_type} ... 🔄 Using reflection")

        agent = ReflectionAgent()
        result = agent.run(
            user_msg=section_prompt,
            generation_system_prompt=f"You are generating the {section_type} section of a legal document.",
            n_steps=config.get("max_steps", 3),
            verbose=verbose
        )
        return {
            "section_type": section_type,
            "content": result["content"],
            "method": "reflection",
            "iterations": result["iterations"],
            "approved": result["approved"]
        }
    else:
        if verbose:
            print(f"📄 {section_type} ... ⚡ Direct generation")

        response = llm.chat(
            messages=[{"role": "user", "content": section_prompt}],
            system=f"You are a legal document assistant. Generate the {section_type} section professionally."
        )
        return {
            "section_type": section_type,
            "content": response.choices[0].message.content or "",
            "method": "direct",
            "iterations": 1,
            "approved": True
        }


# Section templates by document type
SECTIONS_BY_DOCTYPE = {
    "NDA": [
        "header", "parties", "definitions", "confidential_info",
        "obligations", "exclusions", "term_termination", "remedies",
        "general_provisions", "signatures"
    ],
    "EMPLOYMENT": [
        "header", "parties", "recitals", "position_duties",
        "compensation", "benefits", "termination", "non_compete",
        "intellectual_property", "confidentiality", "general_provisions", "signatures"
    ],
    "SERVICE": [
        "header", "parties", "recitals", "scope_of_work",
        "payment_terms", "timeline", "liability", "termination",
        "intellectual_property", "general_provisions", "signatures"
    ],
    "LEASE": [
        "header", "parties", "property_description", "rent_terms",
        "security_deposit", "maintenance", "rules", "termination",
        "general_provisions", "signatures"
    ]
}

DEFAULT_SECTIONS = ["header", "parties", "terms", "obligations", "general_provisions", "signatures"]


def generate_full_document(context: dict, verbose: bool = False) -> Generator[dict, None, None]:
    """
    Generate a complete legal document section by section.

    Uses selective reflection based on document type - critical sections
    get reviewed, simple sections are generated directly.

    Args:
        context: Document data (parties, terms, etc.)
        verbose: Print progress

    Yields:
        dict with section info and content as each section completes
    """
    # Get sections based on document type
    document_type = context.get("document_type", "NDA")
    sections = SECTIONS_BY_DOCTYPE.get(document_type, DEFAULT_SECTIONS)
    critical_sections = CRITICAL_SECTIONS_BY_DOCTYPE.get(document_type, {}).get("critical", DEFAULT_CRITICAL_SECTIONS)

    full_document = []
    total_iterations = 0

    yield {
        "type": "start",
        "total_sections": len(sections),
        "document_type": document_type,
        "critical_sections": critical_sections
    }

    for i, section_type in enumerate(sections):
        uses_reflection = section_type in critical_sections
        yield {
            "type": "section_start",
            "section": section_type,
            "index": i + 1,
            "total": len(sections),
            "uses_reflection": uses_reflection
        }

        result = generate_section(section_type, context, verbose=verbose)
        full_document.append(result["content"])
        total_iterations += result["iterations"]

        yield {
            "type": "section_complete",
            "section": section_type,
            "content": result["content"],
            "method": result["method"],
            "iterations": result["iterations"]
        }

    # Combine all sections
    complete_document = "\n\n".join(full_document)

    yield {
        "type": "document_complete",
        "content": complete_document,
        "total_sections": len(sections),
        "total_iterations": total_iterations
    }
