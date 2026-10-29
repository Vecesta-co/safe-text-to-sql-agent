# DEVLOG.md — Development Log

### Problem 1: SQLite URI read-only on Windows backslash paths
- **Issue**: `file:C:\Users\...\chinook.db?mode=ro` fails — Windows backslashes break the URI scheme.
- **Resolution**: Added explicit path normalization: `os.path.abspath(db_path).replace("\\", "/")` before constructing the `file://` URI.

### Problem 2: String literal keyword injection bypass
- **Issue**: Simple regex for forbidden keywords like `DROP` would fire on `WHERE name = 'DROP THE BEAT'`, rejecting valid read-only queries.
- **Resolution**: Built a `remove_sql_comments_and_strings()` pre-processor that strips all `'...'` quoted literals and `--` / `/* */` comments before structural token analysis.

### Problem 3: PRAGMA introspection vs user PRAGMA queries
- **Issue**: Internal schema introspection uses `PRAGMA table_info()` but we want user-submitted `PRAGMA` queries blocked.
- **Resolution**: Separated internal introspection (uses its own dedicated connection in `schema.py`) from user-facing validation pipeline which blocks `PRAGMA` tokens.
