# PLAN.md — Safe Text-to-SQL Agent

## 1. Executive Summary
A production-grade, injection-proof natural language to SQL agent with multi-layer security validation, real schema introspection, and an embedded read-only REST query studio.

## 2. Competitive Analysis
- **Reference**: `vanna-ai/vanna` (MIT). Vanna relies on LLM outputs and vector search over DDL/questions to generate SQL — it has no structural security validator, no limit enforcement, and requires external vector stores and LLM API keys.
- **Vecesta Differentiator**: Structural AST token scanning (not LLM-based) provides deterministic security guarantees; URI read-only SQLite blocks writes at the OS level; ships with a real Chinook music store database; zero external API dependencies.

## 3. Architecture
```
User Query (NL or SQL) → NL Translator → AST Validator → Read-Only SQLite → ASCII / JSON Result
                                                    ↓ rejected
                                             Security Violation Report
```

## 4. Security Model
- Token whitelist: structural SQL tokens are inspected against a forbidden keyword set AFTER stripping all string literals and comments
- Multi-statement detection: blocks `;`-separated injections
- LIMIT enforcement: queries without LIMIT get default 50; queries exceeding 100 are clamped
- URI mode=ro: SQLite connection refuses writes at connection level
