# Safe Text-to-SQL Agent

[![CI](https://github.com/Vecesta-co/safe-text-to-sql-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Vecesta-co/safe-text-to-sql-agent/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> **AST-validated, read-only Text-to-SQL agent with schema introspection, multi-pattern natural language translation, injection-proof security guardrails, and an embedded REST studio — powered by a real Chinook music store database.**

---

## Terminal Preview

```
Processing: "Show top 5 tracks by price"...

✓ Generated SQL: SELECT name, genre, unit_price FROM tracks ORDER BY unit_price DESC LIMIT 5;
Execution Time : 0.83 ms (5 rows)

+-----+----------------------------------------+-----------+-----------+
| track_id | name                          | genre     | unit_price|
+-----+----------------------------------------+-----------+-----------+
| 13  | Bohemian Rhapsody                     | Rock      | 1.49      |
| 9   | Stairway to Heaven                    | Rock      | 1.49      |
| 14  | Time                                  | Rock      | 1.29      |
+-----+----------------------------------------+-----------+-----------+
```

---

## Key Features

- **Multi-Layer Security Guardrails**:
  - AST structural token analysis stripping all string literals before keyword scanning.
  - Rejects any non-SELECT statement: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `PRAGMA`, `EXEC`, and 15+ others.
  - Multi-statement injection prevention (`;` followed by second statement).
  - LIMIT clamping: automatically enforces safe row count caps.
- **Read-Only Enforcement**:
  - SQLite URI `?mode=ro` connection ensuring OS-level write blocking even if validator is bypassed.
- **Schema Introspection**:
  - Auto-discovers tables, columns, data types, primary keys, foreign keys, and row counts via `PRAGMA table_info` and `PRAGMA foreign_key_list`.
- **Natural Language Translation**:
  - Pattern-matching translator covers sales, revenue, tracks, artists, albums, customers, genres, invoices, and more.
- **Embedded Sample Database**:
  - Ships with a fully seeded Chinook-style music store SQLite database (artists, albums, tracks, customers, invoices).
- **REST API Studio**:
  - Embedded HTTP server with interactive HTML5 query studio, JSON `/query` endpoint, schema explorer, and validation endpoint.

---

## Architecture

```
User Query (NL or SQL)
         │
         ▼
┌─────────────────────────────────────┐
│    Natural Language Translator      │
│  Pattern-match → Template SQL       │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│     AST Security Validator          │
│  - Strip strings & comments         │
│  - Token whitelist enforcement      │
│  - LIMIT clamping                   │
│  - Multi-statement injection guard  │
└──────────────────┬──────────────────┘
                   │ validated SQL only
                   ▼
┌─────────────────────────────────────┐
│   Read-Only SQLite Connection       │
│   file:///path.db?mode=ro URI       │
└──────────────────┬──────────────────┘
                   │
                   ▼
          JSON / ASCII Table
```

---

## Quick Start

```bash
git clone https://github.com/Vecesta-co/safe-text-to-sql-agent.git
cd safe-text-to-sql-agent
pip install -e ".[dev]"

# List tables in the bundled Chinook music store DB
safe-sql tables

# Run a natural language query
safe-sql query "Top 5 tracks by price"
safe-sql query "Sales revenue by country"
safe-sql query "Count total customers"

# Validate any SQL against security rules
safe-sql validate "SELECT name FROM artists"
safe-sql validate "DROP TABLE artists"  # → rejected

# Launch interactive web studio
safe-sql serve --port 8080
```

---

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Interactive HTML5 query studio |
| `POST` | `/query` | `{"query": "natural language"}` or `{"sql": "SELECT ..."}` → JSON result |
| `POST` | `/validate` | `{"sql": "..."}` → validation result with reasons |
| `GET` | `/schema` | Full database schema introspection JSON |
| `GET` | `/tables` | Summary of tables and row counts |
| `GET` | `/health` | Health status |

---

## Why This Is Different and More Capable

| Feature | Vanna AI | LlamaIndex SQL | **safe-text-to-sql-agent** |
|---|---|---|---|
| **Security Model** | LLM prompt-based | LLM prompt-based | **AST structural token scanning + URI read-only** |
| **String Literal Injection** | Vulnerable (LLM hallucination) | Vulnerable | **Strips literals before keyword scan** |
| **Dependencies** | OpenAI/chroma/pgvector | LlamaIndex, OpenAI | **Pure Python stdlib + Pydantic** |
| **Bundled Sample DB** | Requires external setup | Requires external setup | **Ships with seeded Chinook DB** |
| **LIMIT Enforcement** | No | No | **Clamped to configurable max (100 default)** |
| **Multi-statement Guard** | No | No | **Explicit `;` injection detection** |

---

## Difficulties Faced & Solutions

1. **SQLite URI read-only mode on Windows**: Absolute paths with backslashes failed the `file://` URI scheme. Fixed by normalizing paths: `path.replace("\\", "/")`.
2. **String literal keyword injection**: An early validator checking raw SQL for `DROP` would fire on `WHERE name = 'DROP THE BEAT'`. Fixed by stripping all quoted string literals before structural analysis.
3. **PRAGMA blocking**: `PRAGMA table_info` is used internally for introspection but should be blocked in user queries — resolved by separating introspection connections from the user-facing read-only validator pipeline.

---

## Testing

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 Vecesta.co.

---

## Contact

Built by **Vecesta.co**
Email: [vecesta.co@gmail.com](mailto:vecesta.co@gmail.com)
LinkedIn: [vansh-dhawan-2625v](https://www.linkedin.com/in/vansh-dhawan-2625v)
GitHub: [Vecesta-co](https://github.com/Vecesta-co)
X: [@Vansh_Dhawann](https://x.com/Vansh_Dhawann)
Hugging Face: [Vecesta](https://huggingface.co/Vecesta)
