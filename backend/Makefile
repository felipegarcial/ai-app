.PHONY: setup install run dev clean test venv format lint

# Variables
PYTHON = python3
PIP = pip3
FLASK_APP = app.py
VENV = venv
VENV_PIP = $(VENV)/bin/pip
VENV_PYTHON = $(VENV)/bin/python

# Full setup: create venv and install dependencies
setup: venv
	$(VENV_PIP) install -r requirements.txt
	@echo "✅ Setup complete. Run 'source venv/bin/activate' to activate"

# Install dependencies (assumes venv is active)
install:
	$(PIP) install -r requirements.txt

# Run production server
run:
	$(PYTHON) $(FLASK_APP)

# Run development server with reload
dev:
	FLASK_DEBUG=1 $(PYTHON) $(FLASK_APP)

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v

# Create virtual environment
venv:
	$(PYTHON) -m venv venv
	@echo "Run 'source venv/bin/activate' to activate"

# Format code
format:
	black .
	isort .

# Lint code
lint:
	flake8 .
