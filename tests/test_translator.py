from src.schema import introspect_schema
from src.translator import translate_nl_to_sql

DB_PATH = "fixtures/chinook.db"

def test_translate_top_tracks():
    schema = introspect_schema(DB_PATH)
    sql = translate_nl_to_sql("Show top 5 tracks by price", schema)
    assert "SELECT" in sql
    assert "tracks" in sql
    assert "LIMIT 5" in sql

def test_translate_sales_by_country():
    schema = introspect_schema(DB_PATH)
    sql = translate_nl_to_sql("Total sales by country", schema)
    assert "billing_country" in sql
    assert "SUM" in sql

def test_translate_customer_count():
    schema = introspect_schema(DB_PATH)
    sql = translate_nl_to_sql("How many customers do we have?", schema)
    assert "COUNT(*)" in sql
    assert "customers" in sql

def test_translate_albums_by_artist():
    schema = introspect_schema(DB_PATH)
    sql = translate_nl_to_sql("Show albums by AC/DC", schema)
    assert "albums" in sql
    # Translator lowercases artist name in LIKE clause
    assert "ac/dc" in sql.lower()

