from src.validator import validate_and_sanitize_sql

def test_valid_select_query():
    res = validate_and_sanitize_sql("SELECT * FROM tracks")
    assert res.is_valid
    assert "LIMIT 50" in res.sanitized_sql

def test_clamp_large_limit():
    res = validate_and_sanitize_sql("SELECT * FROM tracks LIMIT 5000", max_limit=100)
    assert res.is_valid
    assert "LIMIT 100" in res.sanitized_sql

def test_reject_drop_table():
    res = validate_and_sanitize_sql("DROP TABLE customers")
    assert not res.is_valid
    assert any("Forbidden" in r or "SELECT" in r for r in res.reasons)

def test_reject_delete_and_update():
    res1 = validate_and_sanitize_sql("DELETE FROM invoices WHERE invoice_id = 1")
    assert not res1.is_valid

    res2 = validate_and_sanitize_sql("UPDATE tracks SET unit_price = 0.0")
    assert not res2.is_valid

def test_reject_insert():
    res = validate_and_sanitize_sql("INSERT INTO artists (name) VALUES ('Hacker')")
    assert not res.is_valid

def test_reject_multi_statement_injection():
    res = validate_and_sanitize_sql("SELECT 1; DROP TABLE customers")
    assert not res.is_valid
    assert any("Multi-statement" in r or "Forbidden" in r for r in res.reasons)

def test_reject_pragma():
    res = validate_and_sanitize_sql("PRAGMA table_info(artists)")
    assert not res.is_valid

def test_valid_select_with_string_containing_keyword():
    # 'DROP' inside a quoted string literal should be allowed!
    res = validate_and_sanitize_sql("SELECT name FROM tracks WHERE name = 'DROP THE BEAT'")
    assert res.is_valid

