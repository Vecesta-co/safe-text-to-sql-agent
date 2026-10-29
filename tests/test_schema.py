import os
from src.schema import introspect_schema, format_schema_prompt

DB_PATH = "fixtures/chinook.db"

def test_introspect_schema():
    schema = introspect_schema(DB_PATH)
    assert "artists" in schema.tables
    assert "albums" in schema.tables
    assert "tracks" in schema.tables
    assert "customers" in schema.tables
    assert "invoices" in schema.tables

    artists_table = schema.tables["artists"]
    col_names = [c.name for c in artists_table.columns]
    assert "artist_id" in col_names
    assert "name" in col_names
    assert artists_table.row_count > 0

def test_format_schema_prompt():
    schema = introspect_schema(DB_PATH)
    prompt = format_schema_prompt(schema)
    assert "DATABASE SCHEMA" in prompt
    assert "CREATE TABLE tracks" in prompt
    assert "FOREIGN KEY" in prompt

