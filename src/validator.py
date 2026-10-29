import re
from typing import List, Tuple
from .models import ValidationResult

FORBIDDEN_KEYWORDS = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "REPLACE",
    "CREATE", "ATTACH", "DETACH", "PRAGMA", "VACUUM", "REINDEX", "GRANT",
    "REVOKE", "EXEC", "EXECUTE", "CALL", "SET", "BEGIN", "COMMIT", "ROLLBACK",
    "WRITABLE_SCHEMA"
}

def remove_sql_comments_and_strings(sql: str) -> str:
    """Strip string literals and comments to inspect structural tokens cleanly."""
    # Remove single line comments
    clean = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
    # Remove block comments
    clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)
    # Remove quoted string literals
    clean = re.sub(r"'(?:''|[^'])*'", "''", clean)
    clean = re.sub(r'"(?:""|[^"])*"', '""', clean)
    return clean

def validate_and_sanitize_sql(sql: str, default_limit: int = 50, max_limit: int = 100) -> ValidationResult:
    """Validate that query is strictly a single, read-only SELECT statement."""
    reasons: List[str] = []
    trimmed = sql.strip().rstrip(";")

    if not trimmed:
        return ValidationResult(is_valid=False, sanitized_sql="", reasons=["Empty SQL query provided"])

    # Inspect structural tokens
    structural = remove_sql_comments_and_strings(trimmed).upper()
    tokens = [tok for tok in re.findall(r"\b[A-Z_]+\b", structural)]

    if not tokens:
        return ValidationResult(is_valid=False, sanitized_sql="", reasons=["No recognizable SQL tokens found"])

    # 1. Must start with SELECT or WITH
    if tokens[0] not in ("SELECT", "WITH"):
        return ValidationResult(
            is_valid=False,
            sanitized_sql="",
            reasons=[f"Queries must begin with SELECT or WITH, received: {tokens[0]}"]
        )

    # 2. Check for forbidden keywords anywhere in structural tokens
    found_forbidden = set(tokens) & FORBIDDEN_KEYWORDS
    if found_forbidden:
        return ValidationResult(
            is_valid=False,
            sanitized_sql="",
            reasons=[f"Forbidden write or DDL keywords detected: {', '.join(sorted(found_forbidden))}"]
        )

    # 3. Check for multi-statement execution (; followed by statement)
    # Check if there are semicolons in the structural string
    if ";" in structural:
        parts = [p.strip() for p in structural.split(";") if p.strip()]
        if len(parts) > 1:
            return ValidationResult(
                is_valid=False,
                sanitized_sql="",
                reasons=["Multi-statement queries separated by ';' are strictly forbidden for security"]
            )

    # 4. Enforce or clamp LIMIT clause
    sanitized = trimmed
    limit_match = re.search(r"\bLIMIT\s+(\d+)\b", sanitized, re.IGNORECASE)
    if limit_match:
        val = int(limit_match.group(1))
        if val > max_limit:
            sanitized = re.sub(r"\bLIMIT\s+\d+\b", f"LIMIT {max_limit}", sanitized, flags=re.IGNORECASE)
            reasons.append(f"Clamped LIMIT from {val} to maximum permitted {max_limit}")
    else:
        sanitized = f"{sanitized} LIMIT {default_limit}"
        reasons.append(f"Enforced default LIMIT {default_limit}")

    return ValidationResult(
        is_valid=True,
        sanitized_sql=sanitized,
        reasons=reasons
    )

