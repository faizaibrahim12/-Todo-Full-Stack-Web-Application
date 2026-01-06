"""Start backend and keep running."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "main.py"],
    cwd="D:\\Hackathon-Phase2\\backend",
    capture_output=True,
    text=True,
    timeout=60
)
print("STDOUT:", result.stdout[:2000] if result.stdout else "None")
print("STDERR:", result.stderr[:1000] if result.stderr else "None")
print("Return code:", result.returncode)
