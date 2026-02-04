from flask import Blueprint, request, jsonify, Response
from .service import ChatService
from .state import ConversationState
import json
import time
import re
import threading

chat_bp = Blueprint("chat", __name__)

# Thread-safe session storage
# In production, use Redis or database
_sessions: dict[str, ChatService] = {}
_sessions_lock = threading.Lock()

# Input validation constants
MAX_MESSAGE_LENGTH = 10000  # 10k characters max
MAX_SESSION_ID_LENGTH = 64
SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    def __init__(self, message: str, field: str):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_message(message: str) -> str:
    """Validate and sanitize user message."""
    if not message:
        raise ValidationError("Message is required", "message")

    if not isinstance(message, str):
        raise ValidationError("Message must be a string", "message")

    message = message.strip()

    if len(message) == 0:
        raise ValidationError("Message cannot be empty", "message")

    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValidationError(
            f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters",
            "message"
        )

    return message


def validate_session_id(session_id: str) -> str:
    """Validate session ID format."""
    if not session_id:
        return "default"

    if not isinstance(session_id, str):
        raise ValidationError("Session ID must be a string", "session_id")

    if len(session_id) > MAX_SESSION_ID_LENGTH:
        raise ValidationError(
            f"Session ID exceeds maximum length of {MAX_SESSION_ID_LENGTH}",
            "session_id"
        )

    if not SESSION_ID_PATTERN.match(session_id):
        raise ValidationError(
            "Session ID can only contain letters, numbers, underscores, and hyphens",
            "session_id"
        )

    return session_id


def get_or_create_session(session_id: str) -> ChatService:
    """Get existing session or create new one (thread-safe)."""
    with _sessions_lock:
        if session_id not in _sessions:
            _sessions[session_id] = ChatService()
        return _sessions[session_id]


def sse_event(event_type: str, data: dict) -> str:
    """Format data as SSE event with event type"""
    data["type"] = event_type
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


@chat_bp.route("/", methods=["POST"])
def chat():
    """
    Handle chat message (non-streaming).

    Request body:
        - message: User's message
        - session_id: Session identifier (optional)

    Returns:
        - response: Assistant's response
        - state: Current conversation state
    """
    data = request.get_json()

    # Validate inputs
    try:
        message = validate_message(data.get("message", ""))
        session_id = validate_session_id(data.get("session_id", "default"))
    except ValidationError as e:
        return jsonify({
            "error": e.message,
            "field": e.field,
            "code": "VALIDATION_ERROR"
        }), 400

    start_time = time.time()
    service = get_or_create_session(session_id)
    response = service.chat(message)
    elapsed_time = time.time() - start_time

    return jsonify({
        "response": response,
        "state": service.get_state(),
        "metadata": {
            "elapsed_time_ms": round(elapsed_time * 1000, 2),
            "session_id": session_id
        }
    })


def estimate_tokens(text: str) -> int:
    """
    Estimate token count from text.
    Approximation: ~4 characters per token for English text.
    """
    if not text:
        return 0
    # More accurate: count words and punctuation
    # Average English word is ~4-5 chars, plus spaces
    # Tokens are roughly words + punctuation
    words = len(text.split())
    chars = len(text)
    # Blend word count and char count for better estimate
    return max(1, (words + chars // 4) // 2)


@chat_bp.route("/stream", methods=["POST"])
def chat_stream():
    """
    Handle chat message with SSE streaming.

    SSE Event Types:
        - message: Regular conversational tokens
        - function_call: When model invokes a function (name, arguments)
        - function_result: Results from function execution (name, result)
        - document_update: Document content changes (content, section, action)
        - metadata: Token counts, timing, phase info
        - error: Error states with recovery information
        - done: Stream complete with final state

    Request body:
        - message: User's message
        - session_id: Session identifier (optional)

    Returns:
        SSE stream of response chunks
    """
    data = request.get_json()

    # Validate inputs
    try:
        message = validate_message(data.get("message", ""))
        session_id = validate_session_id(data.get("session_id", "default"))
    except ValidationError as e:
        return jsonify({
            "error": e.message,
            "field": e.field,
            "code": "VALIDATION_ERROR"
        }), 400

    service = get_or_create_session(session_id)

    def generate():
        """Generate SSE events with full function calling support"""
        start_time = time.time()
        total_chars = 0
        function_calls_count = 0
        full_response = ""

        try:
            # Send metadata event at start
            yield sse_event("metadata", {
                "status": "started",
                "phase": service.state.phase.value,
                "session_id": session_id,
                "timestamp": time.time()
            })

            # Process streaming events from service
            for event in service.chat_stream(message):
                event_type = event.get("type")
                event_data = event.get("data")

                if event_type == "content":
                    # Regular content chunk
                    chunk = event_data if isinstance(event_data, str) else str(event_data)
                    total_chars += len(chunk)
                    full_response += chunk
                    yield sse_event("message", {"content": chunk})

                elif event_type == "function_call":
                    # Model is calling a function
                    function_calls_count += 1
                    yield sse_event("function_call", {
                        "name": event_data["name"],
                        "arguments": event_data["arguments"]
                    })

                elif event_type == "function_result":
                    # Function execution completed
                    yield sse_event("function_result", {
                        "name": event_data["name"],
                        "result": event_data["result"]
                    })

                elif event_type == "document_update":
                    # Document content was modified
                    yield sse_event("document_update", {
                        "content": event_data.get("content", ""),
                        "section": event_data.get("section"),
                        "action": event_data.get("action")
                    })

                elif event_type == "done":
                    # Stream complete - send final events
                    elapsed_time = time.time() - start_time

                    # Estimate tokens from accumulated response
                    estimated_tokens = estimate_tokens(full_response)

                    # Send final metadata
                    yield sse_event("metadata", {
                        "status": "completed",
                        "token_count_estimated": estimated_tokens,
                        "char_count": total_chars,
                        "function_calls": function_calls_count,
                        "elapsed_time_ms": round(elapsed_time * 1000, 2)
                    })

                    # Send completion event with final state
                    yield sse_event("done", {
                        "state": service.get_state(),
                        "response": event_data.get("content", "")
                    })

        except ValidationError as e:
            yield sse_event("error", {
                "message": e.message,
                "field": e.field,
                "code": "VALIDATION_ERROR",
                "recoverable": True,
                "suggestion": "Check your input and try again"
            })
        except Exception as e:
            yield sse_event("error", {
                "message": str(e),
                "code": "INTERNAL_ERROR",
                "recoverable": True,
                "suggestion": "Try again or reset the session"
            })

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@chat_bp.route("/state", methods=["GET"])
def get_state():
    """Get current conversation state"""
    try:
        session_id = validate_session_id(request.args.get("session_id", "default"))
    except ValidationError as e:
        return jsonify({
            "error": e.message,
            "field": e.field,
            "code": "VALIDATION_ERROR"
        }), 400

    service = get_or_create_session(session_id)
    return jsonify(service.get_state())


@chat_bp.route("/reset", methods=["POST"])
def reset():
    """Reset conversation state"""
    data = request.get_json() or {}

    try:
        session_id = validate_session_id(data.get("session_id", "default"))
    except ValidationError as e:
        return jsonify({
            "error": e.message,
            "field": e.field,
            "code": "VALIDATION_ERROR"
        }), 400

    with _sessions_lock:
        if session_id in _sessions:
            del _sessions[session_id]

    return jsonify({"message": "Session reset", "session_id": session_id})
