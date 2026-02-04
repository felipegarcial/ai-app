from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import json
from config import Config
from features.chat.routes import chat_bp
from features.export.routes import export_bp
from prompts.composer import compose_prompt
from prompts.patterns import generate_section, generate_full_document

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend
CORS(app, origins=Config.CORS_ORIGINS)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix="/api/chat")
app.register_blueprint(export_bp, url_prefix="/api/export")


@app.route("/")
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Legal AI Backend is running"
    })


@app.route("/api/test-prompt")
def test_prompt():
    """Test endpoint to verify Jinja2 prompt composition"""
    prompt = compose_prompt(
        phase="intake",
        context={
            "document_type": "NDA",
            "expertise": "beginner",
            "collected_data": {"party_a": "Acme Corp"},
            "missing_fields": ["party_b", "duration", "scope"]
        }
    )
    return Response(prompt, mimetype="text/plain")


@app.route("/api/generate-section", methods=["POST"])
def api_generate_section():
    """
    Generate a single document section.
    Uses reflection for critical sections, direct generation for simple ones.
    """
    data = request.get_json()
    section_type = data.get("section_type", "header")
    context = data.get("context", {})

    result = generate_section(section_type, context, verbose=False)

    return jsonify(result)


@app.route("/api/generate-document", methods=["POST"])
def api_generate_document():
    """
    Generate a complete document with SSE streaming progress.
    """
    data = request.get_json()
    context = data.get("context", {})

    def generate():
        for update in generate_full_document(context, verbose=False):
            yield f"data: {json.dumps(update)}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.route("/api/generate-document-sync", methods=["POST"])
def api_generate_document_sync():
    """
    Generate a complete document (non-streaming, returns when complete).
    """
    data = request.get_json()
    context = data.get("context", {})

    sections = []
    total_iterations = 0

    for update in generate_full_document(context, verbose=False):
        if update["type"] == "section_complete":
            sections.append({
                "section": update["section"],
                "content": update["content"],
                "method": update["method"],
                "iterations": update["iterations"]
            })
            total_iterations += update["iterations"]
        elif update["type"] == "document_complete":
            return jsonify({
                "document": update["content"],
                "sections": sections,
                "total_iterations": total_iterations
            })

    return jsonify({"error": "Generation failed"}), 500


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=5000)
