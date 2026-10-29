import os
import sqlite3
import pytest
from src.database import create_sample_chinook_db, get_readonly_connection

def test_create_and_connect_chinook(tmp_path):
    db_file = str(tmp_path / "test_chinook.db")
    create_sample_chinook_db(db_file)
    assert os.path.exists(db_file)

    with get_readonly_connection(db_file) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM artists;")
        count = cur.fetchone()[0]
        assert count > 0

def test_readonly_connection_blocks_writes(tmp_path):
    db_file = str(tmp_path / "test_ro.db")
    create_sample_chinook_db(db_file)

    with get_readonly_connection(db_file) as conn:
        cur = conn.cursor()
        with pytest.raises(sqlite3.OperationalError):
            cur.execute("INSERT INTO artists (name) VALUES ('Hacker Band');")

