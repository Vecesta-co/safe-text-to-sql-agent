from src.executor import SafeSQLExecutor, render_ascii_table

DB_PATH = "fixtures/chinook.db"

def test_executor_natural_query():
    exec = SafeSQLExecutor(DB_PATH)
    res = exec.execute_query(natural_query="List all artists")
    assert res.error is None
    assert res.row_count > 0
    assert "name" in res.columns
    assert res.execution_time_ms >= 0.0

def test_executor_raw_sql_safe():
    exec = SafeSQLExecutor(DB_PATH)
    res = exec.execute_query(raw_sql="SELECT name, genre FROM tracks WHERE genre = 'Rock'")
    assert res.error is None
    assert res.row_count > 0

def test_executor_blocks_malicious_query():
    exec = SafeSQLExecutor(DB_PATH)
    res = exec.execute_query(raw_sql="DROP TABLE albums")
    assert res.error is not None
    assert "Security Violation" in res.error

def test_render_ascii_table():
    cols = ["id", "name"]
    rows = [[1, "AC/DC"], [2, "Queen"]]
    rendered = render_ascii_table(cols, rows)
    assert "+-" in rendered
    assert "AC/DC" in rendered
    assert "Queen" in rendered

