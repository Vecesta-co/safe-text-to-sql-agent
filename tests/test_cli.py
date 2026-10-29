import subprocess
import sys
import os

PYTHON = sys.executable

def run_cli(args):
    return subprocess.run(
        [PYTHON, "-m", "src.cli"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=os.path.join(os.path.dirname(__file__), "..")
    )

def test_cli_help():
    res = run_cli(["--help"])
    assert res.returncode == 0
    assert "safe-sql" in res.stdout.lower() or "usage" in res.stdout.lower()

def test_cli_tables():
    res = run_cli(["tables"])
    assert res.returncode == 0
    assert "artists" in res.stdout
    assert "tracks" in res.stdout

def test_cli_schema():
    res = run_cli(["schema"])
    assert res.returncode == 0
    assert "CREATE TABLE" in res.stdout

def test_cli_query_natural():
    res = run_cli(["query", "Top 3 tracks by price"])
    assert res.returncode == 0
    assert "Generated SQL" in res.stdout
    assert "tracks" in res.stdout

def test_cli_validate_safe():
    res = run_cli(["validate", "SELECT * FROM artists"])
    assert res.returncode == 0
    assert "Valid Read-Only Query" in res.stdout

def test_cli_validate_reject_drop():
    res = run_cli(["validate", "DROP TABLE artists"])
    assert res.returncode != 0
    assert "REJECTED BY SECURITY" in res.stdout

