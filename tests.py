import ast
import subprocess
import sys
from utilities import get_file_count, get_db_env


prompt_inputs = [
    {
        "name": "Test Invalid DB",
        "arg": ["-db", "foo", "-a", "list"],
        "expected": {"fd": "stderr", "out": ["Invalid database selection"]},
    },
    {
        "name": "Test Invalid Firebase DB Action",
        "arg": ["-db", "firebase", "-a", "foo"],
        "expected": {"fd": "stderr", "out": ["Invalid database action"]},
    },
    {
        "name": "Test Invalid Mongodb DB Action",
        "arg": ["-db", "mongodb", "-a", "foo"],
        "expected": {"fd": "stderr", "out": ["Invalid database action"]},
    },
    {
        "name": "Test Invalid Firebase DB Environment",
        "arg": ["-db", "firebase", "-a", "list", "-env", "foo"],
        "expected": {"fd": "stderr", "out": ["Invalid database environment"]},
    },
    {
        "name": "Test Missing Firebase DB Environment",
        "arg": ["-db", "firebase", "-a", "list"],
        "expected": {"fd": "stderr", "out": ["Environment required for Firebase"]},
    },
]
mongodb_inputs = [
    {
        "name": "Test List Collections",
        "arg": ["-db", "mongodb", "-a", "list"],
        "expected": {
            "fd": "stdout",
            "out": [["config", "index", "properties_and_companies", "reviews", "sitemap"]],
        },
    },
    {
        "name": "Test Verbose Mongodb List",
        "arg": ["-db", "mongodb", "-a", "list", "-v"],
        "expected": {
            "fd": "stdout",
            "out": [
                "Initialized connection to mongodb",
                ["config", "index", "properties_and_companies", "reviews", "sitemap"],
            ],
        },
    },
    {
        "name": "Test Seeding Mongodb",
        "arg": ["-db", "mongodb", "-a", "seed"],
        "pre": ["-db", "mongodb", "-a", "clear"],
        "expected": {"fd": "stdout", "out": [""]},
    },
    {
        "name": "Test Seeding Mongodb Verbose",
        "arg": ["-db", "mongodb", "-a", "seed", "-v"],
        "pre": ["-db", "mongodb", "-a", "clear", "-v"],
        "expected": {
            "fd": "stdout",
            "out": [
                "Initialized connection to mongodb",
                "Created index on mongodb for articles",
                f"Seeded mongodb with {get_file_count('articles')} records from articles",
                "Squashed config in mongodb",
                "Squashed sitemap in mongodb"
            ],
        },
    },
    {
        "name": "Test Clearing Mongodb",
        "arg": ["-db", "mongodb", "-a", "clear"],
        "expected": {"fd": "stdout", "out": [""]},
    },
    {
        "name": "Test Clearing Mongodb Verbose",
        "arg": ["-db", "mongodb", "-a", "clear", "-v"],
        "pre": ["-db", "mongodb", "-a", "seed", "-v"],
        "expected": {
            "fd": "stdout",
            "out": ["Initialized connection to mongodb", "Cleared mongodb"],
        },
    },
    {
        "name": "Test Re-Seeding Mongodb",
        "arg": ["-db", "mongodb", "-a", "re-seed"],
        "pre": ["-db", "mongodb", "-a", "seed"],
        "expected": {"fd": "stdout", "out": [""]},
    },
    {
        "name": "Test Re-Seeding Mongodb Verbose",
        "arg": ["-db", "mongodb", "-a", "re-seed", "-v"],
        "expected": {
            "fd": "stdout",
            "out": [
                "Initialized connection to mongodb",
                "Cleared mongodb",
                "Created index on mongodb for articles",
                f"Seeded mongodb with {get_file_count('articles')} records from articles",
                "Squashed config in mongodb",
                "Squashed sitemap in mongodb"
            ],
        },
    },
]
firebase_inputs = [
    {
        "name": "Test Firebase Test Env Collection List",
        "arg": ["-db", "firebase", "-a", "list", "-env", "test"],
        "expected": {
            "fd": "stdout",
            "out": [["config", "index", "properties_and_companies", "reviews", "sitemap"]],
        },
    },
    {
        "name": "Test Firebase Test Env Collection List Verbose",
        "arg": ["-db", "firebase", "-a", "list", "-env", "test", "-v"],
        "expected": {
            "fd": "stdout",
            "out": [
                f"Firebase Certificate: {get_db_env('test')}",
                "Initialized connection to firebase",
                ["config", "index", "properties_and_companies", "reviews", "sitemap"],
            ],
        },
    },
    {
        "name": "Test Seeding Firebase Test Env",
        "arg": ["-db", "firebase", "-a", "seed", "-env", "test"],
        "pre": ["-db", "firebase", "-a", "clear", "-env", "test"],
        "expected": {"fd": "stdout", "out": [""]},
    },
    {
        "name": "Test Seeding Firebase Test Env Verbose",
        "arg": ["-db", "firebase", "-a", "seed", "-env", "test", "-v"],
        "pre": ["-db", "firebase", "-a", "clear", "-env", "test", "-v"],
        "expected": {
            "fd": "stdout",
            "out": [
                f"Firebase Certificate: {get_db_env('test')}",
                "Initialized connection to firebase",
                "Created index on firebase for articles",
                f"Seeded firebase with {get_file_count('articles')} records from articles",
                "Squashed config in firebase",
                "Squashed sitemap in firebase",
            ],
        },
    },
    {
        "name": "Test Clearing Firebase Test Env",
        "arg": ["-db", "firebase", "-a", "clear", "-env", "test"],
        "pre": ["-db", "firebase", "-a", "seed", "-env", "test"],
        "expected": {"fd": "stdout", "out": [""]},
    },
    {
        "name": "Test Clearing Firebase Verbose",
        "arg": ["-db", "firebase", "-a", "clear", "-env", "test", "-v"],
        "pre": ["-db", "firebase", "-a", "seed", "-env", "test", "-v"],
        "expected": {
            "fd": "stdout",
            "out": [
                f"Firebase Certificate: {get_db_env('test')}",
                "Initialized connection to firebase",
                "Cleared firebase",
            ],
        },
    },
    {
        "name": "Test Re-Seeding Firebase Test Env",
        "arg": ["-db", "firebase", "-a", "re-seed", "-env", "test"],
        "pre": ["-db", "firebase", "-a", "seed", "-env", "test"],
        "expected": {"fd": "stdout", "out": [""]},
    },
    {
        "name": "Test Re-Seeding Firebase Test Env Verbose",
        "arg": ["-db", "firebase", "-a", "re-seed", "-env", "test", "-v"],
        "expected": {
            "fd": "stdout",
            "out": [
                f"Firebase Certificate: {get_db_env('test')}",
                "Initialized connection to firebase",
                "Cleared firebase",
                "Created index on firebase for articles",
                f"Seeded firebase with {get_file_count('articles')} records from articles",
                "Squashed config in firebase",
                "Squashed sitemap in firebase"
            ],
        },
    },
]


def subprocess_exec(args):
    command = [sys.executable, "seed.py"] + args
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()
    process.terminate()
    process.wait()
    return stdout, stderr


def exec_with_args(inputs):
    print()
    for test in inputs:
        arg_list = test["arg"]
        expected = test["expected"]
        print(test["name"])
        if "pre" in test:
            stdout, stderr = subprocess_exec(test["pre"])
            if stderr:
                print(stderr)
                exit(-1)

        stdout, stderr = subprocess_exec(arg_list)
        if expected["fd"] == "stdout":
            stdout_arr = stdout.strip().split("\n")
            for idx, out in enumerate(stdout_arr):
                if len(out) > 0 and "[" in out[0]:
                    input_arr = ast.literal_eval(out)
                    for x in input_arr:
                        assert x in expected["out"][idx]
                else:
                    assert out == expected["out"][idx]
        else:
            stderr_arr = stderr.strip().split("\n")
            for idx, err in enumerate(stderr_arr):
                assert err == expected["out"][idx]


def test_params():
    exec_with_args(prompt_inputs)


def test_mongodb():
    exec_with_args(mongodb_inputs)


def test_firebase():
    exec_with_args(firebase_inputs)
