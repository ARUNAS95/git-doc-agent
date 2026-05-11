from fastapi import FastAPI, Request
from dotenv import load_dotenv
from master_agent import run_pipeline

load_dotenv()

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    # Extract repo and commits from webhook payload
    repo_full_name = payload.get("repository", {}).get("full_name", "unknown")
    commits = payload.get("commits", [])
    ref = payload.get("after", "main")  # commit SHA

    print(f"\n[Server] Webhook received for repo: {repo_full_name}")
    print(f"[Server] Commits received: {len(commits)}")

    # Collect all changed Java files across commits
    changed_files = []
    for commit in commits:
        added = commit.get("added", [])
        modified = commit.get("modified", [])
        changed_files += [f for f in added + modified if f.endswith(".java")]

    # Remove duplicates
    changed_files = list(set(changed_files))
    print(f"[Server] Changed Java files: {changed_files}")

    if not changed_files:
        return {"status": "skipped", "reason": "No Java files changed"}

    # Hand off to master agent
    result = run_pipeline(
        repo_full_name=repo_full_name,
        changed_files=changed_files,
        ref=ref
    )

    return result


@app.get("/")
async def root():
    return {"status": "git-doc-agent running"}