"""
OpenAI LLM client with retry logic and error handling.
"""

import time
import logging
from typing import Generator
from openai import OpenAI, APIError, RateLimitError, APITimeoutError, APIConnectionError
from config import Config


# Configure logging
logger = logging.getLogger(__name__)

# Initialize client
client = OpenAI(api_key=Config.OPENAI_API_KEY)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s
RETRYABLE_ERRORS = (RateLimitError, APITimeoutError, APIConnectionError)


class LLMError(Exception):
    """Custom exception for LLM errors with context."""
    def __init__(self, message: str, error_type: str, retryable: bool = False):
        self.message = message
        self.error_type = error_type
        self.retryable = retryable
        super().__init__(self.message)


def chat(
    messages: list,
    system: str = "",
    tools: list = None,
    stream: bool = False
):
    """
    Send a chat request to OpenAI with retry logic.

    Args:
        messages: List of message dicts with 'role' and 'content'
        system: System prompt
        tools: List of tool definitions for function calling
        stream: Whether to stream the response

    Returns:
        Response object or stream iterator

    Raises:
        LLMError: If all retries fail or non-retryable error occurs
    """
    # Prepend system message
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    kwargs = {
        "model": Config.OPENAI_MODEL,
        "max_tokens": Config.MAX_TOKENS,
        "messages": full_messages,
        "stream": stream
    }

    # Convert tools to OpenAI format
    if tools:
        kwargs["tools"] = _convert_tools(tools)

    # Retry loop with exponential backoff
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(**kwargs)
            if attempt > 0:
                logger.info(f"LLM request succeeded after {attempt + 1} attempts")
            return response

        except RETRYABLE_ERRORS as e:
            last_error = e
            error_type = type(e).__name__

            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                logger.warning(
                    f"LLM request failed ({error_type}), "
                    f"retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})"
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"LLM request failed after {MAX_RETRIES} attempts: {error_type}"
                )

        except APIError as e:
            # Non-retryable API error
            logger.error(f"LLM API error (non-retryable): {e}")
            raise LLMError(
                message=str(e),
                error_type="API_ERROR",
                retryable=False
            )

    # All retries exhausted
    raise LLMError(
        message=f"Request failed after {MAX_RETRIES} attempts: {last_error}",
        error_type="MAX_RETRIES_EXCEEDED",
        retryable=True
    )


def stream_chat(
    messages: list,
    system: str = "",
    tools: list = None
) -> Generator[str, None, None]:
    """
    Stream a chat response from OpenAI.
    Yields content chunks as they arrive.
    """
    response = chat(messages, system, tools, stream=True)

    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def _convert_tools(tools: list) -> list:
    """Convert tool schemas to OpenAI format"""
    openai_tools = []
    for tool in tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"]
            }
        })
    return openai_tools
