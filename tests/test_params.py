import subprocess
import sys

inputs = [
    {
        "arg": ["-db", "mongodb", "-a", "list"],
        "expected": {
            "fd": "stdout",
            "out": "['config', 'index', 'properties_and_companies', 'reviews']"
        }
    }
]

def clean_input(input_str):
    return input_str.replace('\n', '').strip()


def test_execute_seed_script_with_popen():
    command = [sys.executable, "seed.py", "-db", "mongodb", "-a", "list"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    print(stdout, stderr)
