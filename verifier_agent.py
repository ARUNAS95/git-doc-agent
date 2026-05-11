# Sub Agent 3: Verifier Agent
# Verifies generated documentation against source code for consistency

import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()


def verify_documentation(file_path: str, source_code: str, documentation: str) -> dict:
    """
    Verifies that generated documentation is consistent with source code.

    Args:
        file_path: path of the Java file
        source_code: original Java source code
        documentation: generated documentation to verify

    Returns:
        dict with file_path, is_valid, issues, and verified_documentation
    """
    if not source_code or not documentation:
        print(f"[VerifierAgent] Skipping {file_path} — missing source or documentation")
        return {
            "file_path": file_path,
            "is_valid": False,
            "issues": ["Missing source code or documentation"],
            "verified_documentation": None
        }

    prompt = f"""You are a senior code reviewer. 
Your task is to verify that the documentation accurately reflects the source code.

Check for:
1. Are all public methods documented?
2. Are parameter names and types correct?
3. Are return types accurately described?
4. Is the class/interface purpose correctly described?
5. Are there any hallucinated methods or fields in the documentation that don't exist in the code?

Java file: {file_path}

Source code:
{source_code}

Generated documentation:
{documentation}

Respond in this exact JSON format:
{{
  "is_valid": true or false,
  "issues": ["issue 1", "issue 2"] or [],
  "corrected_documentation": "corrected markdown documentation here or same as input if valid"
}}

Return only the JSON. No extra text.
"""

    print(f"[VerifierAgent] Verifying documentation for {file_path}...")

    response = completion(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()

    try:
        import json
        result = json.loads(raw)
        is_valid = result.get("is_valid", False)
        issues = result.get("issues", [])
        corrected_doc = result.get("corrected_documentation", documentation)

        if is_valid:
            print(f"[VerifierAgent] {file_path} — documentation verified ✅")
        else:
            print(f"[VerifierAgent] {file_path} — issues found: {issues}")

        return {
            "file_path": file_path,
            "is_valid": is_valid,
            "issues": issues,
            "verified_documentation": corrected_doc
        }

    except Exception as e:
        print(f"[VerifierAgent] Failed to parse verification response for {file_path}: {e}")
        return {
            "file_path": file_path,
            "is_valid": False,
            "issues": [f"Verification parsing failed: {str(e)}"],
            "verified_documentation": documentation
        }


def verify_batch(file_contents: list, documentation_results: list) -> list:
    """
    Verifies documentation for multiple files.

    Args:
        file_contents: list of dicts with file_path and content
        documentation_results: list of dicts with file_path and documentation

    Returns:
        list of verification results
    """
    content_map = {item["file_path"]: item.get("content") for item in file_contents}
    results = []

    for doc_result in documentation_results:
        file_path = doc_result.get("file_path")
        documentation = doc_result.get("documentation")
        source_code = content_map.get(file_path)
        result = verify_documentation(file_path, source_code, documentation)
        results.append(result)

    return results