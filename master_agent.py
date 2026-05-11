# Master Agent: Orchestrator
# Receives changed Java files from webhook and coordinates all sub agents

import os
import json
from dotenv import load_dotenv

from code_reader_agent import read_multiple_files
from doc_generator_agent import generate_documentation_batch
from verifier_agent import verify_batch

load_dotenv()


def run_pipeline(repo_full_name: str, changed_files: list, ref: str = "main") -> dict:
    """
    Master orchestrator that runs the full documentation pipeline.

    Steps:
    1. Code Reader Agent — fetches Java file contents from GitHub
    2. Doc Generator Agent — generates documentation using LLM
    3. Verifier Agent — verifies documentation against source code

    Args:
        repo_full_name: GitHub repo in "owner/repo" format
        changed_files: list of changed Java file paths
        ref: branch or commit SHA

    Returns:
        dict with pipeline results per file
    """
    print(f"\n[MasterAgent] Starting pipeline for {len(changed_files)} Java file(s) in {repo_full_name}")
    print(f"[MasterAgent] Files: {changed_files}\n")

    if not changed_files:
        print("[MasterAgent] No Java files to process. Exiting.")
        return {"status": "skipped", "reason": "No Java files changed", "results": []}

    # Step 1 — Code Reader Agent
    print("[MasterAgent] Step 1: Reading file contents...")
    file_contents = read_multiple_files(repo_full_name, changed_files, ref)

    readable = [f for f in file_contents if f.get("content")]
    failed_reads = [f for f in file_contents if not f.get("content")]

    if failed_reads:
        print(f"[MasterAgent] Warning: {len(failed_reads)} file(s) could not be read")

    if not readable:
        print("[MasterAgent] No readable files. Exiting pipeline.")
        return {"status": "failed", "reason": "Could not read any files", "results": []}

    # Step 2 — Documentation Generator Agent
    print(f"\n[MasterAgent] Step 2: Generating documentation for {len(readable)} file(s)...")
    documentation_results = generate_documentation_batch(readable)

    successful_docs = [d for d in documentation_results if d.get("documentation")]
    if not successful_docs:
        print("[MasterAgent] No documentation generated. Exiting pipeline.")
        return {"status": "failed", "reason": "Documentation generation failed", "results": []}

    # Step 3 — Verifier Agent
    print(f"\n[MasterAgent] Step 3: Verifying documentation for {len(successful_docs)} file(s)...")
    verification_results = verify_batch(readable, successful_docs)

    # Compile final results
    final_results = []
    for verification in verification_results:
        file_path = verification["file_path"]
        final_results.append({
            "file_path": file_path,
            "is_valid": verification["is_valid"],
            "issues": verification["issues"],
            "documentation": verification["verified_documentation"]
        })

    valid_count = sum(1 for r in final_results if r["is_valid"])
    print(f"\n[MasterAgent] Pipeline complete.")
    print(f"[MasterAgent] {valid_count}/{len(final_results)} files passed verification ✅")

    return {
        "status": "success",
        "repo": repo_full_name,
        "total_files": len(changed_files),
        "processed": len(final_results),
        "verified": valid_count,
        "results": final_results
    }