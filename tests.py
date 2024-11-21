import ast
import subprocess
import sys
from utilities import get_file_count

inputs = [
    {
        "name": "Test List Collections",
        "arg": ["-db", "mongodb", "-a", "list"],
        "expected": {
            "fd": "stdout",
            "out": [['config', 'index', 'properties_and_companies', 'reviews']]
        }
    },
    {
        "name": "Test Invalid DB",
        "arg": ["-db", "foo", "-a", "list"],
        "expected": {
            "fd": "stderr",
            "out": ["Invalid database selection"]
        }
    },
    {
        "name": "Test Invalid Firebase DB Action",
        "arg": ["-db", "firebase", "-a", "foo"],
        "expected": {
            "fd": "stderr",
            "out": ["Invalid database action"]
        }
    },
    {
        "name": "Test Invalid Firebase DB Environment",
        "arg": ["-db", "firebase", "-a", "list", "-env", "foo"],
        "expected": {
            "fd": "stderr",
            "out": ["Invalid database environment"]
        }
    },
    {
        "name": "Test Missing Firebase DB Environment",
        "arg": ["-db", "firebase", "-a", "list"],
        "expected": {
            "fd": "stderr",
            "out": ["Environment required for Firebase"]
        }
    },
    {
        "name": "Test Verbose Mongodb List",
        "arg": ["-db", "mongodb", "-a", "list", '-v'],
        "expected": {
            "fd": "stdout",
            "out": ["Initialized connection to mongodb", ['config', 'index', 'properties_and_companies', 'reviews']]
        }
    },
    {
        "name": "Test Seeding Mongodb",
        "arg": ["-db", "mongodb", "-a", "seed"],
        "pre": ["-db", "mongodb", "-a", "clear"],
        "expected": {
            "fd": "stdout",
            "out": [""]
        }
    },
    {
        "name": "Test Seeding Mongodb Verbose",
        "arg": ["-db", "mongodb", "-a", "seed", "-v"],
        "pre": ["-db", "mongodb", "-a", "clear", "-v"],
        "expected": {
            "fd": "stdout",
            "out": ["Initialized connection to mongodb","Cleared mongodb","Created index on mongodb for articles",f"Seeded mongodb with {get_file_count('articles')} records from articles", "Squashed config in mongodb"]
        }
    },
    {
        "name": "Test Clearing Mongodb",
        "arg": ["-db", "mongodb", "-a", "clear"],
        "expected": {
            "fd": "stdout",
            "out": [""]
        }
    },
    {
        "name": "Test Clearing Mongodb Verbose",
        "arg": ["-db", "mongodb", "-a", "clear", "-v"],
        "pre": ["-db", "mongodb", "-a", "seed", "-v"],
        "expected": {
            "fd": "stdout",
            "out": ["Initialized connection to mongodb","Cleared mongodb"]
        }
    },
    {
        "name": "Test Re-Seeding Mongodb",
        "arg": ["-db", "mongodb", "-a", "re-seed"],
        "pre": ["-db", "mongodb", "-a", "seed"],
        "expected": {
            "fd": "stdout",
            "out": [""]
        }
    },
    {
        "name": "Test Re-Seeding Mongodb Verbose",
        "arg": ["-db", "mongodb", "-a", "re-seed", "-v"],
        "pre": ["-db", "mongodb", "-a", "seed", "-v"],
        "expected": {
            "fd": "stdout",
            "out": ["Initialized connection to mongodb","Cleared mongodb","Created index on mongodb for articles",f"Seeded mongodb with {get_file_count('articles')} records from articles", "Squashed config in mongodb"]
        }
    },

]

def clean_input(input_str):
    return input_str.replace('\n', '').strip()


def test_parameters():
    print()
    for test in inputs:
        arg_list = test['arg']
        expected = test['expected']
        print(test['name'])
        if 'pre' in test :
            print("Executing pre-test task...")
            cmd = [sys.executable, "seed.py"] + test['pre']
            process = subprocess.Popen(cmd)
            stdout, stderr = process.communicate()
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
                exit(-1)

        command = [sys.executable, "seed.py"] + arg_list
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if expected['fd'] == "stdout":
            stdout_arr = stdout.strip().split('\n')
            for idx, out in enumerate(stdout_arr):
                if len(out) > 0 and '[' in out[0]:
                    input_arr = ast.literal_eval(out)
                    for x in input_arr:
                        assert x in expected['out'][idx]
                else:
                    assert out == expected['out'][idx]
        else:
            stderr_arr = stderr.strip().split("\n")
            for idx, err in enumerate(stderr_arr):
                assert err == expected['out'][idx]


