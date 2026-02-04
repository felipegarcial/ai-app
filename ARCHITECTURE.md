# System Architecture

This document describes the architecture of the Legal Document Generation System.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Diagram](#2-component-diagram)
3. [Data Flow](#3-data-flow)
4. [API Design](#4-api-design)
5. [Error Handling Strategy](#5-error-handling-strategy)
6. [Scalability Considerations](#6-scalability-considerations)

---

## 1. System Overview

The Legal Document Generation System is a conversational AI application that assists users in creating legal documents (NDAs) through natural dialogue. The system uses a multi-layer prompt architecture with selective reflection for quality assurance.

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python / Flask |
| LLM Provider | OpenAI GPT-4o |
| Streaming | Server-Sent Events (SSE) |
| Templating | Jinja2 |
| Frontend | React (separate) |

### Key Features

- **Conversational Interface**: Natural dialogue for gathering requirements
- **Multi-Phase Workflow**: Intake → Clarification → Generation → Revision
- **Selective Reflection**: Quality assurance on critical document sections
- **Real-time Streaming**: Token-by-token response delivery
- **Function Calling**: Structured data extraction and validation

---

## 2. Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  CLIENT                                      │
│                            (React Frontend)                                  │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                                      │ HTTP/SSE
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               FLASK APP                                      │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   /api/chat     │  │ /api/generate-  │  │  /api/generate-document    │  │
│  │                 │  │    section      │  │                             │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┬──────────────┘  │
│           │                    │                          │                  │
│           └────────────────────┼──────────────────────────┘                  │
│                                │                                             │
│                                ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        FEATURES/CHAT                                  │   │
│  │                                                                       │   │
│  │   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │   │
│  │   │  routes.py  │───▶│ service.py  │───▶│  state.py   │              │   │
│  │   │             │    │             │    │             │              │   │
│  │   │ - /         │    │ - chat()    │    │ - phase     │              │   │
│  │   │ - /stream   │    │ - chat_     │    │ - collected │              │   │
│  │   │ - /state    │    │   stream()  │    │   _data     │              │   │
│  │   │ - /reset    │    │             │    │ - history   │              │   │
│  │   └─────────────┘    └──────┬──────┘    └─────────────┘              │   │
│  │                             │                                         │   │
│  └─────────────────────────────┼─────────────────────────────────────────┘   │
│                                │                                             │
│           ┌────────────────────┼────────────────────┐                        │
│           │                    │                    │                        │
│           ▼                    ▼                    ▼                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │    PROMPTS      │  │     TOOLS       │  │      LLM        │              │
│  │                 │  │                 │  │                 │              │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │  ┌───────────┐  │              │
│  │ │ composer.py │ │  │ │ schemas.py  │ │  │  │  llm.py   │  │              │
│  │ └─────────────┘ │  │ └─────────────┘ │  │  └─────┬─────┘  │              │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │        │        │              │
│  │ │ templates/  │ │  │ │ handlers.py │ │  │        │        │              │
│  │ │  - base.j2  │ │  │ └─────────────┘ │  │        │        │              │
│  │ │  - legal.j2 │ │  └─────────────────┘  │        │        │              │
│  │ │  - phases/  │ │                       │        │        │              │
│  │ └─────────────┘ │                       │        │        │              │
│  │ ┌─────────────┐ │                       │        │        │              │
│  │ │ patterns/   │ │                       │        │        │              │
│  │ │ reflection  │ │                       │        │        │              │
│  │ └─────────────┘ │                       │        │        │              │
│  └─────────────────┘                       └────────┼────────┘              │
│                                                     │                        │
└─────────────────────────────────────────────────────┼────────────────────────┘
                                                      │
                                                      ▼
                                          ┌─────────────────────┐
                                          │    OpenAI API       │
                                          │    (GPT-4o)         │
                                          └─────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **routes.py** | HTTP endpoints, request/response handling |
| **service.py** | Business logic, orchestration |
| **state.py** | Conversation state management |
| **composer.py** | Jinja2 prompt composition |
| **templates/** | Prompt templates (4 layers) |
| **patterns/** | Advanced techniques (Reflection) |
| **schemas.py** | Function calling definitions |
| **handlers.py** | Function execution logic |
| **validation.py** | Schema validation & fallback extraction |
| **llm.py** | OpenAI API client |

---

## 3. Data Flow

### 3.1 Conversation Flow (Chat with Multi-Turn Tool Calling)

```
┌──────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐     ┌─────────┐
│Client│────▶│ routes.py│────▶│service. │────▶│ composer │────▶│ llm.py  │
│      │     │          │     │   py    │     │   .py    │     │         │
└──────┘     └──────────┘     └─────────┘     └──────────┘     └────┬────┘
                                   │                                 │
                                   ▼                                 │
                              ┌─────────┐                           │
                              │state.py │                           │
                              │         │                           │
                              │ phase   │                           │
                              │ data    │                           │
                              │ history │                           │
                              └─────────┘                           │
                                   ▲                                 │
                                   │          ┌─────────────────────┘
                                   │          │
                                   │          ▼
                                   │    ┌──────────────┐
                                   │    │ Tool Calls?  │
                                   │    └──────┬───────┘
                                   │           │
                                   │     Yes   │   No
                                   │    ┌──────┴──────┐
                                   │    │             │
                                   │    ▼             ▼
                              ┌────┴────┐     ┌──────────┐
                              │handlers │     │ Response │
                              │   .py   │     │  (done)  │
                              └────┬────┘     └──────────┘
                                   │
                                   ▼
                              ┌─────────────────────────┐
                              │ Add tool result to      │
                              │ history, loop back to   │
                              │ LLM for natural response│
                              └─────────────────────────┘

Multi-Turn Tool Calling Loop:
1. User message → LLM
2. LLM returns tool_calls → Execute handlers
3. Tool results added to history
4. History sent back to LLM
5. LLM generates natural language response
6. Response returned to client
```

### 3.2 Document Generation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DOCUMENT GENERATION FLOW                            │
└─────────────────────────────────────────────────────────────────────────┘

    ┌───────────┐
    │  Client   │
    │  Request  │
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │  Context  │  party_a, party_b, duration, etc.
    │   Data    │
    └─────┬─────┘
          │
          ▼
    ┌───────────────────────────────────────────────────────────────┐
    │                   FOR EACH SECTION                             │
    │                                                                │
    │   ┌─────────────────────────────────────────────────────────┐ │
    │   │              CHECK SECTION_CONFIG                        │ │
    │   └───────────────────────┬─────────────────────────────────┘ │
    │                           │                                    │
    │              ┌────────────┴────────────┐                      │
    │              │                         │                      │
    │              ▼                         ▼                      │
    │   ┌─────────────────┐      ┌─────────────────────────┐       │
    │   │ use_reflection: │      │   use_reflection:       │       │
    │   │     FALSE       │      │       TRUE              │       │
    │   │                 │      │                         │       │
    │   │  Direct LLM     │      │  ┌─────────────────┐    │       │
    │   │  Generation     │      │  │   GENERATE      │    │       │
    │   │                 │      │  └────────┬────────┘    │       │
    │   │  (1 API call)   │      │           │             │       │
    │   │                 │      │           ▼             │       │
    │   └────────┬────────┘      │  ┌─────────────────┐    │       │
    │            │               │  │    REFLECT      │    │       │
    │            │               │  └────────┬────────┘    │       │
    │            │               │           │             │       │
    │            │               │           ▼             │       │
    │            │               │     ┌──────────┐        │       │
    │            │               │     │  <OK>?   │        │       │
    │            │               │     └────┬─────┘        │       │
    │            │               │          │              │       │
    │            │               │    Yes   │   No         │       │
    │            │               │    ┌─────┴─────┐        │       │
    │            │               │    │           │        │       │
    │            │               │    ▼           │        │       │
    │            │               │  Done      Loop back    │       │
    │            │               │           to GENERATE   │       │
    │            │               │  (2-6 API calls)        │       │
    │            │               └─────────────────────────┘       │
    │            │                          │                      │
    │            └──────────────────────────┘                      │
    │                           │                                   │
    │                           ▼                                   │
    │                  ┌─────────────────┐                         │
    │                  │ Section Content │                         │
    │                  └─────────────────┘                         │
    │                                                               │
    └───────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   COMBINE SECTIONS    │
                    │                       │
                    │   Header + Parties +  │
                    │   Definitions + ...   │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   COMPLETE DOCUMENT   │
                    └───────────────────────┘
```

### 3.3 Phase State Machine

```
                    ┌─────────────────┐
                    │     START       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     INTAKE      │◀──────────────────┐
                    │                 │                   │
                    │ Gather info     │    Missing        │
                    │ Ask questions   │    fields         │
                    └────────┬────────┘                   │
                             │                            │
                             │ All fields collected       │
                             ▼                            │
                    ┌─────────────────┐                   │
                    │  CLARIFICATION  │───────────────────┘
                    │                 │   Needs more info
                    │ Verify data     │
                    │ Check conflicts │
                    └────────┬────────┘
                             │
                             │ Confirmed
                             ▼
                    ┌─────────────────┐
                    │   GENERATION    │
                    │                 │
                    │ Create document │
                    │ Section by      │
                    │ section         │
                    └────────┬────────┘
                             │
                             │ Document ready
                             ▼
                    ┌─────────────────┐
                    │    REVISION     │◀─────┐
                    │                 │      │
                    │ Apply changes   │      │ More changes
                    │ based on        │──────┘
                    │ feedback        │
                    └────────┬────────┘
                             │
                             │ User satisfied
                             ▼
                    ┌─────────────────┐
                    │      DONE       │
                    └─────────────────┘
```

---

## 4. API Design

### 4.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/test-prompt` | Test prompt composition |
| POST | `/api/chat/` | Send chat message |
| POST | `/api/chat/stream` | Send chat message (SSE) |
| GET | `/api/chat/state` | Get conversation state |
| POST | `/api/chat/reset` | Reset conversation |
| POST | `/api/generate-section` | Generate single section |
| POST | `/api/generate-document` | Generate full document (SSE) |
| POST | `/api/generate-document-sync` | Generate full document (sync) |

### 4.2 Request/Response Examples

**Chat Request:**
```json
POST /api/chat/
{
    "message": "I need an NDA between Apple and Google",
    "session_id": "user-123"
}
```

**Chat Response:**
```json
{
    "response": "I'd be happy to help create an NDA...",
    "state": {
        "phase": "intake",
        "document_type": "NDA",
        "collected_data": {},
        "missing_fields": ["party_a_name", "party_b_name", ...]
    }
}
```

**Document Generation Request:**
```json
POST /api/generate-document-sync
{
    "context": {
        "document_type": "NDA",
        "party_a_name": "Apple Inc.",
        "party_b_name": "Google LLC",
        "confidential_info_type": "source code",
        "duration": "2 years",
        "governing_law": "California"
    }
}
```

### 4.3 SSE Event Types

#### Chat Stream Events (`/api/chat/stream`)

| Event Type | Description | Data |
|------------|-------------|------|
| `metadata` | Status updates | `{"type": "metadata", "status": "started/completed", "phase": "...", "token_count": N}` |
| `message` | Chat response token | `{"type": "message", "content": "..."}` |
| `function_call` | LLM invoking a tool | `{"type": "function_call", "name": "analyze_request", "arguments": "{...}"}` |
| `function_result` | Tool execution result | `{"type": "function_result", "name": "analyze_request", "result": {...}}` |
| `document_update` | Document content changed | `{"type": "document_update", "content": "...", "section": "...", "action": "..."}` |
| `error` | Error occurred | `{"type": "error", "message": "...", "recoverable": true}` |
| `done` | Stream complete | `{"type": "done", "state": {...}, "response": "..."}` |

#### Document Generation Events (`/api/generate-document`)

| Event Type | Description | Data |
|------------|-------------|------|
| `section_start` | Section generation started | `{"type": "section_start", "section": "obligations"}` |
| `section_complete` | Section finished | `{"type": "section_complete", "section": "...", "content": "...", "method": "reflection/direct"}` |
| `document_complete` | Full document ready | `{"type": "document_complete", "content": "..."}` |

---

## 4.4 Structured Output Enforcement

The system implements robust structured output handling with multiple fallback layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│                  STRUCTURED OUTPUT PIPELINE                          │
└─────────────────────────────────────────────────────────────────────┘

   LLM Response (tool_call.arguments)
              │
              ▼
   ┌─────────────────────────┐
   │  1. JSON Parse          │  Try: json.loads(arguments)
   └───────────┬─────────────┘
              │
         Success?
        /         \
      Yes          No
       │            │
       ▼            ▼
   Continue    ┌─────────────────────────┐
               │  2. Extract from        │  Regex patterns for
               │     Markdown/Text       │  ```json blocks, {...}
               └───────────┬─────────────┘
                          │
                     Success?
                    /         \
                  Yes          No
                   │            │
                   ▼            ▼
               Continue    ┌─────────────────────────┐
                          │  3. Free-text           │  Pattern matching
                          │     Extraction          │  for known fields
                          └───────────┬─────────────┘
                                      │
                                      ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                  4. SCHEMA VALIDATION                            │
   │                                                                  │
   │   validate(parsed_data, JSON_SCHEMA)                            │
   │                                                                  │
   │   If fails → attempt_recovery():                                │
   │   - Fix missing required fields with defaults                   │
   │   - Clamp numeric values to valid ranges                        │
   │   - Convert types where possible                                │
   └───────────────────────────────────────────────────────────────────┘
              │
              ▼
   ┌─────────────────────────┐
   │  5. Validated Output    │  Guaranteed to match schema
   └─────────────────────────┘
```

### Implementation (tools/validation.py)

```python
def validate_and_parse_tool_call(tool_name: str, arguments: str) -> dict:
    # Step 1: Try JSON parsing
    parsed = safe_parse_json(arguments)

    # Step 2: Fallback to free-text extraction
    if parsed is None:
        parsed = extract_from_freetext(arguments, tool_name)

    # Step 3: Validate and auto-recover
    validated = validate_tool_input(tool_name, parsed)
    return validated
```

### Fallback Examples

| Scenario | Input | Recovery |
|----------|-------|----------|
| Malformed JSON | `{"intent": "create"` | Extract from text |
| Missing required field | `{"intent": "create"}` | Add defaults |
| Invalid enum value | `{"intent": "CREATE"}` | Map to valid value |
| Out of range | `{"confidence": 1.5}` | Clamp to 1.0 |
| Free text response | `"Create an NDA"` | Pattern extraction |

---

## 5. Error Handling Strategy

### 5.1 Error Categories

| Category | Examples | Handling |
|----------|----------|----------|
| **Validation** | Missing message, invalid JSON | 400 Bad Request |
| **LLM Errors** | API timeout, rate limit | Retry with backoff, 503 |
| **Tool Errors** | Invalid tool input | Return error to LLM |
| **State Errors** | Invalid phase transition | Log and recover |

### 5.2 Error Response Format

```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {}
}
```

### 5.3 LLM Error Recovery

```python
# Retry logic for transient failures
MAX_RETRIES = 3
RETRY_DELAY = [1, 2, 4]  # Exponential backoff

for attempt in range(MAX_RETRIES):
    try:
        response = llm.chat(...)
        break
    except RateLimitError:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY[attempt])
        else:
            raise
```

### 5.4 Graceful Degradation

| Scenario | Fallback |
|----------|----------|
| Reflection fails | Return direct generation |
| Tool call fails | Continue without tool result |
| Streaming fails | Fall back to sync response |

---

## 6. Scalability Considerations

### 6.1 Current Limitations

| Aspect | Current State | Limitation |
|--------|---------------|------------|
| State Storage | In-memory dict | Lost on restart |
| Sessions | Single process | Not distributed |
| Rate Limiting | None | No protection |

### 6.2 Production Recommendations

**State Storage:**
```python
# Current (in-memory)
sessions: dict[str, ChatService] = {}

# Production (Redis)
import redis
r = redis.Redis()
r.setex(f"session:{session_id}", 3600, json.dumps(state))
```

**Horizontal Scaling:**
```
                    ┌─────────────┐
                    │   Load      │
                    │  Balancer   │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │ Flask 1  │    │ Flask 2  │    │ Flask 3  │
     └────┬─────┘    └────┬─────┘    └────┬─────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │  Redis   │
                    │  (State) │
                    └──────────┘
```

**Rate Limiting:**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/api/chat/")
@limiter.limit("10 per minute")
def chat():
    ...
```

### 6.3 Cost Optimization

| Strategy | Implementation |
|----------|----------------|
| Caching | Cache common document sections |
| Smaller models | Use GPT-3.5 for simple tasks |
| Prompt compression | Summarize long histories |
| Batch requests | Combine multiple sections |

---

## Summary

This architecture provides:

1. **Modularity**: Clear separation of concerns between components
2. **Flexibility**: Easy to add new document types or phases
3. **Quality**: Selective reflection for critical sections
4. **Scalability**: Clear path to production deployment
5. **Maintainability**: Well-documented data flows and APIs
