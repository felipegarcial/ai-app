# Legal Document Generation System

A conversational AI system for generating legal documents using advanced prompt engineering techniques.

<img width="1511" height="1307" alt="image" src="https://github.com/user-attachments/assets/6f2199fe-e786-4779-8762-d63f2c3b686b" />


## Features

- **Conversational Interface**: Natural dialogue for gathering document requirements
- **Multi-Phase Workflow**: Intake → Clarification → Generation → Revision
- **Hierarchical Prompt System**: 4-layer prompt architecture with dynamic composition
- **Reflection Pattern**: Self-consistency checking for critical document sections
- **Real-time Streaming**: SSE-based token-by-token response delivery
- **Function Calling**: Structured data extraction and validation
- **Document Export**: PDF, Word, and TXT export options

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.9+ / Flask |
| **Frontend** | React 19 / TypeScript |
| **State Management** | Zustand |
| **Styling** | Tailwind CSS |
| **LLM** | OpenAI GPT-4o |
| **Templating** | Jinja2 |
| **Streaming** | Server-Sent Events (SSE) |

## Project Structure

```
legal_ai/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration management
│   ├── llm.py                 # OpenAI client wrapper with retry logic
│   │
│   ├── features/
│   │   ├── chat/              # Chat feature
│   │   │   ├── routes.py      # API endpoints (REST + SSE)
│   │   │   ├── service.py     # Business logic + tool calling
│   │   │   └── state.py       # Conversation state management
│   │   └── export/            # Document export (PDF, DOCX)
│   │       └── routes.py
│   │
│   ├── prompts/
│   │   ├── composer.py        # Jinja2 prompt composition
│   │   ├── templates/         # Prompt templates (4 layers)
│   │   │   ├── base.j2        # Layer 1: Meta-system
│   │   │   ├── legal.j2       # Layer 2: Legal domain
│   │   │   └── phases/        # Layer 3: Phase-specific
│   │   └── patterns/
│   │       ├── chain_of_thought.py  # CoT scaffolding
│   │       └── reflection.py        # Generate-reflect loop
│   │
│   └── tools/
│       ├── schemas.py         # Function definitions (JSON Schema)
│       ├── handlers.py        # Function execution logic
│       └── validation.py      # Schema validation & fallback
│
├── frontend/
│   ├── src/
│   │   ├── app/               # Main App component + layout
│   │   ├── features/
│   │   │   ├── chat/          # Chat UI + streaming hook
│   │   │   ├── document/      # Document preview + export
│   │   │   └── session/       # Session state + sidebar
│   │   └── shared/
│   │       ├── api/           # API client + SSE streaming
│   │       ├── components/    # UI components (shadcn/ui)
│   │       └── hooks/         # Custom React hooks
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── PROMPT_ENGINEERING.md      # Prompt engineering documentation
├── ARCHITECTURE.md            # System architecture
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- OpenAI API key

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-api-key-here

# Run the server
python app.py
```

Backend runs at: **http://localhost:5000**

### 2. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env
# Default API URL is http://localhost:5000

# Run the development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

### 3. Open the Application

Open your browser and navigate to **http://localhost:5173**

---

## Usage

### Basic Conversation Flow

1. **Start a conversation** with a request like:
   ```
   I need an NDA between TechCorp Inc and StartupXYZ
   ```

2. **Provide information** as the system asks:
   - Party names
   - Type of confidential information
   - Duration
   - Governing law

3. **Review the generated document** in the preview panel

4. **Request revisions** if needed:
   ```
   Change the duration to 5 years
   ```

5. **Export** the document as PDF, Word, or TXT

---

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/
```

### Chat (Non-streaming)
```bash
curl -X POST http://localhost:5000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an NDA between Apple and Google"}'
```

### Chat with Streaming (SSE)
```bash
curl -X POST http://localhost:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "I need an NDA between Apple and Google"}'
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

### Export Document (PDF)
```bash
curl -X POST http://localhost:5000/api/export/pdf \
  -H "Content-Type: application/json" \
  -d '{"content": "Document content...", "title": "NDA Agreement"}' \
  --output document.pdf
```

### Export Document (Word)
```bash
curl -X POST http://localhost:5000/api/export/docx \
  -H "Content-Type: application/json" \
  -d '{"content": "Document content...", "title": "NDA Agreement"}' \
  --output document.docx
```

---

## Conversation Phases

| Phase | Description |
|-------|-------------|
| **Intake** | System gathers required information through conversation |
| **Clarification** | System verifies collected data and resolves conflicts |
| **Generation** | Document is created section by section |
| **Revision** | User can request changes to the generated document |

---

## Advanced Features

### Selective Reflection

Critical sections use a generate-reflect loop for quality assurance. The system automatically determines which sections need reflection based on document type:

**NDA Document:**
| Section | Uses Reflection | Max Iterations |
|---------|-----------------|----------------|
| header | No | 1 |
| parties | No | 1 |
| confidential_info | Yes | 3 |
| obligations | Yes | 3 |
| exclusions | Yes | 2 |
| remedies | Yes | 2 |

### Function Calling

The system uses structured function calling for data extraction:

| Function | Purpose |
|----------|---------|
| `analyze_request` | Parse user intent and detect document type |
| `extract_structured_data` | Extract typed data from conversation |
| `validate_completeness` | Check if ready to generate |
| `generate_document_section` | Create document sections |
| `generate_full_document` | Generate complete document |
| `apply_revision` | Modify existing document |

### SSE Event Types

| Event | Description |
|-------|-------------|
| `message` | Streaming text content |
| `function_call` | LLM invoking a tool |
| `function_result` | Tool execution result |
| `document_update` | Document content changed |
| `metadata` | Token counts, timing info |
| `error` | Error with recovery info |
| `done` | Stream complete |

---

## Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | `gpt-4o` |
| `MAX_TOKENS` | Max response tokens | `4096` |
| `FLASK_DEBUG` | Debug mode | `1` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:5173` |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:5000` |

---

## Development

### Backend Commands

```bash
cd backend
source venv/bin/activate

# Run development server
python app.py

# Or with make
make dev
```

### Frontend Commands

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

---

## Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture and data flows
- [PROMPT_ENGINEERING.md](./PROMPT_ENGINEERING.md) - Prompt engineering approach and iterations

---

## Design Decisions

1. **Hierarchical Prompts**: 4-layer architecture allows for separation of concerns and dynamic composition based on conversation state.

2. **Selective Reflection**: Only critical sections (obligations, remedies) use the generate-reflect loop, balancing quality with response time.

3. **Function Calling**: Structured data extraction ensures consistent state management and enables the LLM to update the conversation state.

4. **SSE Streaming**: Real-time token streaming provides better UX than waiting for complete responses.

5. **In-Memory State**: Session state is stored in memory for simplicity. For production, use Redis or a database.

6. **No Authentication**: Not implemented as per requirements. Add JWT or session-based auth for production.

---

## License

MIT
