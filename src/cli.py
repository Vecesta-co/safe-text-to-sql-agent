import sys
sys.stdout.reconfigure(encoding="utf-8")
import argparse
import os
import json
from colorama import init as colorama_init, Fore, Style
colorama_init()

from .database import create_sample_chinook_db
from .schema import introspect_schema, format_schema_prompt
from .validator import validate_and_sanitize_sql
from .executor import SafeSQLExecutor, render_ascii_table

DEFAULT_DB = "fixtures/chinook.db"

def ensure_db(db_path: str = DEFAULT_DB):
    if not os.path.exists(db_path):
        print(f"{Fore.YELLOW}Creating sample Chinook database at {db_path}...{Style.RESET_ALL}")
        create_sample_chinook_db(db_path)

def cmd_query(args):
    ensure_db(args.db)
    executor = SafeSQLExecutor(args.db)

    print(f"{Fore.CYAN}Processing: \"{args.query}\"...{Style.RESET_ALL}")
    res = executor.execute_query(natural_query=args.query, raw_sql=args.sql)

    if res.error:
        print(f"\n{Fore.RED}✗ {res.error}{Style.RESET_ALL}")
        sys.exit(1)

    print(f"\n{Fore.GREEN}✓ Generated SQL:{Style.RESET_ALL} {res.generated_sql}")
    print(f"{Fore.CYAN}Execution Time :{Style.RESET_ALL} {res.execution_time_ms} ms ({res.row_count} rows)\n")
    print(render_ascii_table(res.columns, res.rows))

def cmd_schema(args):
    ensure_db(args.db)
    schema = introspect_schema(args.db)
    print(f"{Fore.CYAN}=== Database Schema ({args.db}) ==={Style.RESET_ALL}\n")
    print(format_schema_prompt(schema))

def cmd_tables(args):
    ensure_db(args.db)
    schema = introspect_schema(args.db)
    print(f"{Fore.CYAN}{'Table Name':<20} | {'Columns':<8} | {'Rows':<8}{Style.RESET_ALL}")
    print("-" * 42)
    for tname, t in schema.tables.items():
        print(f"{tname:<20} | {len(t.columns):<8} | {t.row_count:<8}")

def cmd_validate(args):
    val = validate_and_sanitize_sql(args.sql)
    if val.is_valid:
        print(f"{Fore.GREEN}✓ Valid Read-Only Query{Style.RESET_ALL}")
        print(f"Sanitized SQL: {val.sanitized_sql}")
        if val.reasons:
            print(f"Notes        : {'; '.join(val.reasons)}")
    else:
        print(f"{Fore.RED}✗ REJECTED BY SECURITY GUARDRAILS{Style.RESET_ALL}")
        for r in val.reasons:
            print(f"  • {r}")
        sys.exit(1)

def cmd_init_db(args):
    create_sample_chinook_db(args.db)
    print(f"{Fore.GREEN}✓ Seeded sample Chinook database at {args.db}{Style.RESET_ALL}")

def cmd_serve(args):
    from .server import run_server
    ensure_db(args.db)
    run_server(port=args.port, db_path=args.db)

def main():
    parser = argparse.ArgumentParser(prog="safe-sql", description="Safe Text-to-SQL Agent by Vecesta.co")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to SQLite database")
    sub = parser.add_subparsers(dest="command", required=True)

    # query
    p_q = sub.add_parser("query", help="Ask natural language question or execute safe SQL")
    p_q.add_argument("query", nargs="?", default="", help="Natural language question")
    p_q.add_argument("--sql", help="Direct SQL query to validate and execute")
    p_q.set_defaults(func=cmd_query)

    # schema
    p_s = sub.add_parser("schema", help="Introspect database schema")
    p_s.set_defaults(func=cmd_schema)

    # tables
    p_t = sub.add_parser("tables", help="List database tables and row counts")
    p_t.set_defaults(func=cmd_tables)

    # validate
    p_v = sub.add_parser("validate", help="Test SQL string against security AST rules")
    p_v.add_argument("sql", help="SQL query to validate")
    p_v.set_defaults(func=cmd_validate)

    # init-db
    p_init = sub.add_parser("init-db", help="Generate fresh sample Chinook database")
    p_init.set_defaults(func=cmd_init_db)

    # serve
    p_srv = sub.add_parser("serve", help="Launch HTTP REST server and studio")
    p_srv.add_argument("--port", type=int, default=8080)
    p_srv.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

