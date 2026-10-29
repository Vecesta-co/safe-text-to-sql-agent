import sqlite3
from typing import Dict, List
from .models import ColumnInfo, ForeignKeyInfo, TableSchema, DatabaseSchema
from .database import get_readonly_connection

def introspect_schema(db_path: str) -> DatabaseSchema:
    """Introspect SQLite database to extract tables, columns, foreign keys, and row counts."""
    tables: Dict[str, TableSchema] = {}

    with get_readonly_connection(db_path) as conn:
        cur = conn.cursor()

        # Get all table names
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        table_names = [row[0] for row in cur.fetchall()]

        for tname in table_names:
            # PRAGMA table_info
            cur.execute(f"PRAGMA table_info({tname});")
            col_rows = cur.fetchall()
            columns = [
                ColumnInfo(
                    name=r[1],
                    data_type=r[2].upper(),
                    not_null=bool(r[3]),
                    default_value=str(r[4]) if r[4] is not None else None,
                    primary_key=bool(r[5])
                )
                for r in col_rows
            ]

            # PRAGMA foreign_key_list
            cur.execute(f"PRAGMA foreign_key_list({tname});")
            fk_rows = cur.fetchall()
            foreign_keys = [
                ForeignKeyInfo(
                    column=r[3],
                    referenced_table=r[2],
                    referenced_column=r[4]
                )
                for r in fk_rows
            ]

            # Count rows
            cur.execute(f"SELECT COUNT(*) FROM {tname};")
            count = cur.fetchone()[0]

            tables[tname] = TableSchema(
                table_name=tname,
                columns=columns,
                foreign_keys=foreign_keys,
                row_count=count
            )

    return DatabaseSchema(database_type="sqlite", tables=tables)

def format_schema_prompt(schema: DatabaseSchema) -> str:
    """Format introspected schema into standard DDL prompt for LLMs or query translation."""
    lines = ["DATABASE SCHEMA (Read-Only):"]
    for tname, tschema in schema.tables.items():
        col_strs = [f"{c.name} {c.data_type}" + (" PRIMARY KEY" if c.primary_key else "") for c in tschema.columns]
        lines.append(f"CREATE TABLE {tname} (")
        for c_str in col_strs:
            lines.append(f"  {c_str},")
        for fk in tschema.foreign_keys:
            lines.append(f"  FOREIGN KEY ({fk.column}) REFERENCES {fk.referenced_table}({fk.referenced_column}),")
        lines.append(");")
        lines.append(f"-- Estimated rows: {tschema.row_count}\n")
    return "\n".join(lines)

