
# Primers S-Form (Primers Intelligence)

## Overview
Primers S-Form is an advanced cognitive engine designed for code intelligence, refactoring, and architectural reasoning. It features a 3-layer cognitive stack (Analysis, Interpretation, Judgment) to "reason" about code structure rather than just processing text.

## Features
- **Cognitive Stack**:
  - **Layer 1 (Analysis)**: AST-based parsing for deep code structure extraction.
  - **Layer 2 (Interpretation)**: Heuristic engine to identify roles (Worker, Coordinator, God Object) and code smells.
  - **Layer 3 (Judgment)**: Decision making on refactoring needs and risk assessment.
- **GitHub Learning**: Ability to ingest and learn from user repositories.
- **Comparative Reasoning**: Compare multiple files for structural complexity.

## Quick Start

### 1. Start the Backend Server
Windows:
```bash
run_backend.bat
```
(Or run manually: `python backend/main.py` - ensure dependencies are installed via `pip install -r backend/requirements.txt`)

### 2. Connect with CLI Client
In a new terminal:
```bash
python cli_client.py
```

## API Usage
- **POST /chat**: Send a command or query.
  - Payload: `{"message": "analyze corpus", "mode": "default"}`
- **POST /ingest**: Ingest data.
  - Payload: `{"target": "github", "params": {"username": "octocat"}}`

## Key Commands (in CLI)
- `analyze corpus`: Run heuristic analysis on the local codebase.
- `compare fileA vs fileB`: Compare two files.
- `learn from github <username>`: Index repositories for a user.

## Local LLM Setup (Ollama)
This project is designed to work with a local LLM for enhanced reasoning.

1. **Install Ollama**: Download from [ollama.com](https://ollama.com).
2. **Pull a Model**: Run `ollama pull llama3`.
3. **Configure**: ensure `backend/.env` points to your Ollama instance (default is `http://localhost:11434/v1/chat/completions`).
4. **Start Backend**: The engine will automatically detect and use the local LLM if it's running.
