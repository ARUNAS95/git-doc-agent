# git-doc-agent

An automated documentation generation system for Java repositories using a multi-agent architecture.

## Overview

git-doc-agent listens to GitHub Webhook events, detects changed Java files, and automatically generates verified documentation using a pipeline of specialized AI agents.

## Architecture

```
GitHub Webhook
      ↓
 server.py (FastAPI)
      ↓
 Master Agent (Orchestrator)
      ↓           ↓           ↓
Code Reader   Doc Generator  Verifier
   Agent          Agent       Agent
(GitHub API)   (LiteLLM)   (LiteLLM)
```

### Master Agent
Orchestrates the full pipeline. Receives changed Java files from the webhook and coordinates all sub-agents in sequence.

### Sub Agent 1 — Code Reader Agent
Fetches the actual content of changed Java files from GitHub using the GitHub Contents API.

### Sub Agent 2 — Documentation Generator Agent
Takes Java source code and generates structured Markdown documentation using LiteLLM.

### Sub Agent 3 — Verifier Agent
Compares generated documentation against source code to catch hallucinations, missing methods, or incorrect parameter descriptions. Returns corrected documentation if issues are found.

## Tech Stack

- Python
- FastAPI
- LiteLLM
- GitHub Webhooks API
- GitHub Contents API
- dotenv

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ARUNAS95/git-doc-agent.git
cd git-doc-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_personal_access_token
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run the server

```bash
uvicorn server:app --reload --port 8000
```

### 5. Expose locally using ngrok (for webhook testing)

```bash
ngrok http 8000
```

Set your GitHub repository webhook URL to:
```
https://<your-ngrok-url>/webhook
```

Content type: `application/json`
Events: `Push`

## How It Works

1. A push is made to a GitHub repository
2. GitHub sends a webhook payload to `/webhook`
3. The server extracts all changed `.java` files
4. The Master Agent runs the pipeline:
    - **Code Reader** fetches file contents via GitHub API
    - **Doc Generator** generates Markdown documentation via LLM
    - **Verifier** validates documentation against source code
5. Verified documentation is returned in the response

## Project Structure

```
git-doc-agent/
├── server.py               # FastAPI webhook receiver
├── master_agent.py         # Orchestrator
├── agents/
│   ├── code_reader_agent.py    # Sub Agent 1
│   ├── doc_generator_agent.py  # Sub Agent 2
│   └── verifier_agent.py       # Sub Agent 3
├── .env                    # Environment variables (not committed)
├── requirements.txt
└── README.md
```
