import re
import subprocess
import os

def extract_command(text):
    # Try extracting from ```bash``` blocks
    match = re.search(r"```(?:bash)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: look for lines starting with typical command patterns
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.startswith(("touch ", "mkdir ", "cd ", "ls ", "rm ", "echo ", "cat ")):
            return line

    return None



def run_command(command):
    """Run a terminal command and return the output or error."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Command failed:\n{e.stderr.strip()}"
    
def search_files(filename_pattern):
    matches = []

    # Determine where to start (platform-safe)
    system = platform.system()
    if system == "Windows":
        drives = [f"{d}:/" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:/")]
        start_dirs = drives
    elif system in ["Linux", "Darwin"]:
        start_dirs = ["/"]
    else:
        return ["❌ Unsupported OS"]
