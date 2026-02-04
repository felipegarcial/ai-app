from typing import Generator
import json
from .state import ConversationState
from prompts.composer import compose_prompt
from tools.schemas import TOOLS
from tools.handlers import handle_tool_call
from tools.validation import validate_and_parse_tool_call
import llm


class ChatService:
    """
    Handles chat logic and LLM interactions.
    Implements multi-turn tool calling with proper OpenAI conversation flow.
    """

    MAX_TOOL_ITERATIONS = 5  # Prevent infinite tool loops

    def __init__(self, state: ConversationState = None):
        self.state = state or ConversationState()

    def chat(self, user_message: str) -> str:
        """
        Process a user message and return assistant response.
        Handles multi-turn tool calling - executes tools and sends results
        back to LLM for natural language response.

        Args:
            user_message: The user's input message

        Returns:
            Assistant's response text
        """
        # Add user message to history
        self.state.add_message("user", user_message)

        # Compose prompt based on current state
        system_prompt = compose_prompt(
            phase=self.state.phase.value,
            context=self.state.to_context()
        )

        # Multi-turn tool calling loop
        for _ in range(self.MAX_TOOL_ITERATIONS):
            response = llm.chat(
                messages=self.state.history,
                system=system_prompt,
                tools=TOOLS
            )

            choice = response.choices[0]

            # If no tool calls, we have the final response
            if choice.finish_reason != "tool_calls" or not choice.message.tool_calls:
                assistant_message = choice.message.content or ""
                self.state.add_message("assistant", assistant_message)
                return assistant_message

            # Process tool calls and continue conversation
            self._execute_tool_calls(choice.message)

        # If we hit max iterations, return last content or error
        return choice.message.content or "[Max tool iterations reached]"

    def chat_stream(self, user_message: str) -> Generator[dict, None, None]:
        """
        Process a user message and stream the response with event types.

        Args:
            user_message: The user's input message

        Yields:
            Event dicts with type and data:
            - {"type": "content", "data": "text chunk"}
            - {"type": "function_call", "data": {"name": ..., "arguments": ...}}
            - {"type": "function_result", "data": {"name": ..., "result": ...}}
            - {"type": "document_update", "data": {"content": ..., "section": ...}}
            - {"type": "done", "data": {"content": "full response"}}
        """
        # Add user message to history
        self.state.add_message("user", user_message)

        # Compose prompt based on current state
        system_prompt = compose_prompt(
            phase=self.state.phase.value,
            context=self.state.to_context()
        )

        full_response = ""

        # Multi-turn tool calling loop for streaming
        for _ in range(self.MAX_TOOL_ITERATIONS):
            # First, try non-streaming to check for tool calls
            response = llm.chat(
                messages=self.state.history,
                system=system_prompt,
                tools=TOOLS
            )

            choice = response.choices[0]

            # If tool calls, handle them and emit events
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    # Emit function_call event
                    yield {
                        "type": "function_call",
                        "data": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }

                    # Execute tool with validated parsing (graceful fallback)
                    tool_input = validate_and_parse_tool_call(
                        tool_call.function.name,
                        tool_call.function.arguments
                    )
                    tool_result = handle_tool_call(
                        tool_name=tool_call.function.name,
                        tool_input=tool_input,
                        state=self.state
                    )

                    # Emit function_result event
                    yield {
                        "type": "function_result",
                        "data": {
                            "name": tool_call.function.name,
                            "result": tool_result
                        }
                    }

                    # Emit document_update if document was modified
                    if tool_call.function.name in ("generate_document_section", "generate_full_document", "apply_revision"):
                        if self.state.current_document:
                            yield {
                                "type": "document_update",
                                "data": {
                                    "content": self.state.current_document,
                                    "title": getattr(self.state, 'document_metadata', {}).get('title', 'Legal Document'),
                                    "section": tool_input.get("section_type") or tool_input.get("target_section"),
                                    "action": tool_call.function.name
                                }
                            }

                # Add tool calls to history and continue
                self._execute_tool_calls(choice.message)
                continue

            # No tool calls - use the response from the first call
            # (Don't make a second streaming call - it's wasteful and can return empty)
            full_response = choice.message.content or ""

            if full_response:
                # Yield the content in chunks for streaming effect
                chunk_size = 20
                for i in range(0, len(full_response), chunk_size):
                    chunk = full_response[i:i + chunk_size]
                    yield {"type": "content", "data": chunk}

            # Add complete response to history
            self.state.add_message("assistant", full_response)

            yield {"type": "done", "data": {"content": full_response}}
            return

        # Max iterations reached
        yield {"type": "done", "data": {"content": full_response or "[Max tool iterations reached]"}}

    def _execute_tool_calls(self, assistant_message) -> list:
        """
        Execute tool calls and add results to conversation history.
        Follows OpenAI's multi-turn conversation format.

        Args:
            assistant_message: The assistant message containing tool_calls

        Returns:
            List of tool results
        """
        # Add assistant message with tool calls to history
        self.state.history.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        # Execute each tool and add results to history
        results = []
        for tool_call in assistant_message.tool_calls:
            # Use validated parsing with graceful fallback
            tool_input = validate_and_parse_tool_call(
                tool_call.function.name,
                tool_call.function.arguments
            )
            tool_result = handle_tool_call(
                tool_name=tool_call.function.name,
                tool_input=tool_input,
                state=self.state
            )

            # Add tool result to history (OpenAI format)
            self.state.history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
            })

            results.append(tool_result)

        return results

    def get_state(self) -> dict:
        """Return current conversation state as dict"""
        return self.state.to_context()
