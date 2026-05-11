# Sub Agent 2: Documentation Generator Agent
# Takes Java source code and generates documentation using LiteLLM

import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()


def generate_documentation(file_path: str, source_code: str) -> dict:
    """
    Generates documentation for a Java file using LiteLLM.

    Args:
        file_path: path of the Java file
        source_code: raw Java source code content

    Returns:
        dict with file_path and generated documentation
    """
    if not source_code:
        print(f"[DocGeneratorAgent] Skipping {file_path} — no source code provided")
        return {"file_path": file_path, "documentation": None, "error": "No source code"}

    prompt = f"""You are a senior software engineer. 
Generate clear, concise documentation for the following Java source file.

Include:
- Class/interface purpose
- Public method descriptions with parameters and return values
- Any important implementation notes

Java file: {file_path}

Source code:
{source_code}

Return only the documentation in Markdown format. No code blocks, just clean Markdown.
"""

    print(f"[DocGeneratorAgent] Generating documentation for {file_path}...")

    response = completion(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )

    documentation = response.choices[0].message.content.strip()
    print(f"[DocGeneratorAgent] Documentation generated for {file_path} ({len(documentation)} chars)")

    return {"file_path": file_path, "documentation": documentation}


def generate_documentation_batch(file_contents: list) -> list:
    """
    Generates documentation for multiple Java files.

    Args:
        file_contents: list of dicts with file_path and content

    Returns:
        list of dicts with file_path and documentation
    """
    results = []
    for file_data in file_contents:
        file_path = file_data.get("file_path")
        content = file_data.get("content")
        result = generate_documentation(file_path, content)
        results.append(result)
    return results