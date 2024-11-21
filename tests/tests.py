import subprocess
import sys

inputs = [
    {
        "arg": ["-db", "mongodb", "-a", "list"],
        "expected": {
            "fd": "stdout",
            "out": "['config', 'index', 'properties_and_companies', 'reviews']"
        }
    },
    {
        "arg": ["-db", "foo", "-a", "list"],
        "expected": {
            "fd": "stderr",
            "out": "Invalid database selection"
        }
    },
    {
        "arg": ["-db", "firebase", "-a", "foo"],
        "expected": {
            "fd": "stderr",
            "out": "Invalid database action"
        }
    },
    {
        "arg": ["-db", "firebase", "-a", "list", "-env", "foo"],
        "expected": {
            "fd": "stderr",
            "out": "Invalid database environment"
        }
    },
    {
        "arg": ["-db", "firebase", "-a", "list"],
        "expected": {
            "fd": "stderr",
            "out": "Environment required for Firebase"
        }
    },
    {
        "arg": ["-db", "mongodb", "-a", "list", '-v'],
        "expected": {
            "fd": "stdout",
            "out": "Initialized connection to mongodb['config', 'index', 'properties_and_companies', 'reviews']"
        }
    },
]

def clean_input(input_str):
    return input_str.replace('\n', '').strip()


def test_parameters():
    for test in inputs:
        arg_list = test['arg']
        print(arg_list)
        expected = test['expected']
        command = [sys.executable, "seed.py"] + arg_list
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        cleaned_stdout = clean_input(stdout)
        cleaned_stderr = clean_input(stderr)
        if expected['fd'] == "stdout":
            assert cleaned_stdout == expected['out']
        else:
            assert cleaned_stderr == expected['out']


