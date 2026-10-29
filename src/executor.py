import time
from typing import Optional, List, Any
from .models import QueryResult, ValidationResult
from .database import get_readonly_connection
from .validator import validate_and_sanitize_sql
from .schema import introspect_schema
from .translator import translate_nl_to_sql

class SafeSQLExecutor:
    """Safe database query coordinator with validation guardrails."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.schema = introspect_schema(db_path)

    def execute_query(
        self,
        natural_query: Optional[str] = None,
        raw_sql: Optional[str] = None
    ) -> QueryResult:
        t0 = time.perf_counter()

        # Step 1: Generate or accept SQL
        if raw_sql:
            generated_sql = raw_sql
            nat_q = natural_query or "Direct SQL query execution"
        elif natural_query:
            nat_q = natural_query
            generated_sql = translate_nl_to_sql(natural_query, self.schema)
        else:
            return QueryResult(
                natural_query="",
                generated_sql="",
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=0.0,
                error="No natural query or raw SQL provided"
            )

        # Step 2: Security & AST Validation
        val_result: ValidationResult = validate_and_sanitize_sql(generated_sql)
        if not val_result.is_valid:
            dt_ms = (time.perf_counter() - t0) * 1000
            return QueryResult(
                natural_query=nat_q,
                generated_sql=generated_sql,
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=round(dt_ms, 2),
                error="Security Violation: " + "; ".join(val_result.reasons)
            )

        sanitized_sql = val_result.sanitized_sql

        # Step 3: Execute in Read-Only Connection
        try:
            with get_readonly_connection(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(sanitized_sql)
                rows = cur.fetchall()
                cols = [desc[0] for desc in cur.description] if cur.description else []
                # Convert rows to serializable lists
                serializable_rows = [[float(v) if isinstance(v, float) else v for v in r] for r in rows]

            dt_ms = (time.perf_counter() - t0) * 1000
            return QueryResult(
                natural_query=nat_q,
                generated_sql=sanitized_sql,
                columns=cols,
                rows=serializable_rows,
                row_count=len(rows),
                execution_time_ms=round(dt_ms, 2),
                error=None
            )
        except Exception as e:
            dt_ms = (time.perf_counter() - t0) * 1000
            return QueryResult(
                natural_query=nat_q,
                generated_sql=sanitized_sql,
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=round(dt_ms, 2),
                error=f"SQL Execution Error: {str(e)}"
            )

def render_ascii_table(columns: List[str], rows: List[List[Any]]) -> str:
    """Render query tabular result into ASCII formatted table."""
    if not columns:
        return "No results returned."

    # Compute column widths
    str_rows = [[str(cell) if cell is not None else "NULL" for cell in r] for r in rows]
    widths = [len(col) for col in columns]
    for r in str_rows:
        for idx, cell in enumerate(r):
            widths[idx] = max(widths[idx], len(cell))

    border = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    header = "|" + "|".join([f" {col:<{widths[idx]}} " for idx, col in enumerate(columns)]) + "|"

    data_lines = []
    for r in str_rows:
        line = "|" + "|".join([f" {cell:<{widths[idx]}} " for idx, cell in enumerate(r)]) + "|"
        data_lines.append(line)

    lines = [border, header, border] + data_lines + [border]
    return "\n".join(lines)

