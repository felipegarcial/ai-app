# Legal Document Generation System

A conversational AI system for generating legal documents (NDAs) using advanced prompt engineering techniques.

## Features

- **Conversational Interface**: Natural dialogue for gathering document requirements
- **Multi-Phase Workflow**: Intake → Clarification → Generation → Revision
- **Hierarchical Prompt System**: 4-layer prompt architecture with dynamic composition
- **Reflection Pattern**: Self-consistency checking for critical document sections
- **Real-time Streaming**: SSE-based token-by-token response delivery
- **Function Calling**: Structured data extraction and validation

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.9+ / Flask |
| LLM | OpenAI GPT-4o |
| Templating | Jinja2 |
| Streaming | Server-Sent Events (SSE) |

## Project Structure

```
legal_ai/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration management
│   ├── llm.py                 # OpenAI client wrapper
│   │
│   ├── features/
│   │   └── chat/              # Chat feature
│   │       ├── routes.py      # API endpoints
│   │       ├── service.py     # Business logic
│   │       └── state.py       # Conversation state
│   │
│   ├── prompts/
│   │   ├── composer.py        # Jinja2 prompt composition
│   │   ├── templates/         # Prompt templates
│   │   │   ├── base.j2        # Layer 1: Meta-system
│   │   │   ├── legal.j2       # Layer 2: Legal domain
│   │   │   └── phases/        # Layer 3: Phase-specific
│   │   └── patterns/
│   │       └── reflection.py  # Reflection pattern
│   │
│   └── tools/
│       ├── schemas.py         # Function definitions
│       ├── handlers.py        # Function execution
│       └── validation.py      # Schema validation & fallback
│
├── PROMPT_ENGINEERING.md      # Prompt engineering documentation
├── ARCHITECTURE.md            # System architecture
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd legal_ai
   ```

2. **Set up the backend**
   ```bash
   cd backend
   make setup
   ```
   This creates a virtual environment and installs dependencies.

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

4. **Run the server**
   ```bash
   source venv/bin/activate
   make dev
   ```
   Server runs at `http://localhost:5000`

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/
```

### Chat (Conversational)
```bash
curl -X POST http://localhost:5000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an NDA between Apple and Google"}'
```

### Chat with Streaming
```bash
curl -X POST http://localhost:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an NDA between Apple and Google"}'
```

### Generate Single Section
```bash
curl -X POST http://localhost:5000/api/generate-section \
  -H "Content-Type: application/json" \
  -d '{
    "section_type": "obligations",
    "context": {
      "document_type": "NDA",
      "party_a_name": "Apple Inc.",
      "party_b_name": "Google LLC",
      "confidential_info_type": "source code and algorithms",
      "duration": "2 years",
      "governing_law": "California"
    }
  }'
```

### Generate Full Document
```bash
curl -X POST http://localhost:5000/api/generate-document-sync \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "document_type": "NDA",
      "party_a_name": "Apple Inc.",
      "party_b_name": "Google LLC",
      "confidential_info_type": "source code and algorithms",
      "duration": "2 years",
      "governing_law": "California"
    }
  }'
```

### Get Conversation State
```bash
curl http://localhost:5000/api/chat/state?session_id=default
```

### Reset Conversation
```bash
curl -X POST http://localhost:5000/api/chat/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "default"}'
```

## Conversation Flow

1. **Intake Phase**: System gathers required information
   - Party names
   - Type of confidential information
   - Duration
   - Governing law

2. **Clarification Phase**: System verifies collected data
   - Checks for conflicts
   - Confirms understanding

3. **Generation Phase**: Document is created
   - Section-by-section generation
   - Selective reflection on critical sections

4. **Revision Phase**: User can request changes
   - Modify specific sections
   - Regenerate as needed

## Advanced Features

### Selective Reflection

Critical sections use a generate-reflect loop for quality assurance:

| Section | Uses Reflection | Max Iterations |
|---------|-----------------|----------------|
| header | No | 1 |
| parties | No | 1 |
| confidential_info | Yes | 3 |
| obligations | Yes | 3 |
| remedies | Yes | 2 |

### Function Calling

The system uses 5 core functions:

1. `analyze_request` - Parse user intent
2. `extract_structured_data` - Extract typed data
3. `validate_completeness` - Check if ready to generate
4. `generate_document_section` - Create document sections
5. `apply_revision` - Modify existing document

## Configuration

Environment variables (`.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | `gpt-4o` |
| `MAX_TOKENS` | Max response tokens | `4096` |
| `FLASK_DEBUG` | Debug mode | `1` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000` |

## Development

### Available Make Commands

```bash
make setup    # Create venv and install dependencies
make dev      # Run development server
make run      # Run production server
make clean    # Remove venv and cache files
make test     # Run tests
```

### Project Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design.

### Prompt Engineering

See [PROMPT_ENGINEERING.md](./PROMPT_ENGINEERING.md) for prompt design documentation.

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture and data flows
- [PROMPT_ENGINEERING.md](./PROMPT_ENGINEERING.md) - Prompt engineering approach

## Assumptions and Decisions

1. **Document Type**: Currently focused on NDA generation. Architecture supports extension to other document types.

2. **No Authentication**: As per requirements, no auth is implemented. In production, add JWT or session-based auth.

3. **In-Memory State**: Session state is stored in memory. For production, use Redis or database.

4. **Single Document Type**: While architecture supports multiple types, only NDA is fully implemented.

## License

MIT
