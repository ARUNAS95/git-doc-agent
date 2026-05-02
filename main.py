import subprocess

def get_changed_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        capture_output=True,
        text=True
    )
    files = result.stdout.strip().split("\n")
    return [f for f in files if f.endswith(".java")]

if __name__ == "__main__":
    changed = get_changed_files()
    print(f"Changed Java files: {changed}")