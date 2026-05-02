from fastapi import FastAPI, Request
from dotenv import load_dotenv
import hmac
import hashlib
import os

load_dotenv()

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    # get repo name and commits
    repo_name = payload.get("repository", {}).get("name", "unknown")
    commits = payload.get("commits", [])

    print(f"\nRepo: {repo_name}")
    print(f"Commits received: {len(commits)}")

    # get all changed java files across commits
    changed_files = []
    for commit in commits:
        added = commit.get("added", [])
        modified = commit.get("modified", [])
        changed_files += [f for f in added + modified if f.endswith(".java")]

    print(f"Changed Java files: {changed_files}")

    return {"status": "received", "java_files": changed_files}

@app.get("/")
async def root():
    return {"status": "git-doc-agent running"}