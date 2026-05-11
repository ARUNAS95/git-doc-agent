# Sub Agent 1: Code Reader Agent
# Reads the actual content of changed Java files from GitHub using the GitHub API

import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def read_java_file(repo_full_name: str, file_path: str, ref: str = "main") -> dict:
    """
    Reads the content of a Java file from a GitHub repository.

    Args:
        repo_full_name: e.g. "ARUNAS95/git-doc-agent"
        file_path: e.g. "src/main/java/com/example/MyService.java"
        ref: branch or commit SHA

    Returns:
        dict with file_path and content
    """
    url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"ref": ref}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"[CodeReaderAgent] Failed to read {file_path}: {response.status_code}")
        return {"file_path": file_path, "content": None, "error": response.json()}

    data = response.json()
    content = base64.b64decode(data["content"]).decode("utf-8")

    print(f"[CodeReaderAgent] Successfully read {file_path} ({len(content)} chars)")
    return {"file_path": file_path, "content": content}


def read_multiple_files(repo_full_name: str, file_paths: list, ref: str = "main") -> list:
    """
    Reads multiple Java files from a GitHub repository.

    Args:
        repo_full_name: GitHub repo in "owner/repo" format
        file_paths: list of file paths to read
        ref: branch or commit SHA

    Returns:
        list of dicts with file_path and content
    """
    results = []
    for file_path in file_paths:
        result = read_java_file(repo_full_name, file_path, ref)
        results.append(result)
    return results