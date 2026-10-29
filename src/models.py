from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ColumnInfo(BaseModel):
    name: str
    data_type: str
    primary_key: bool = False
    not_null: bool = False
    default_value: Optional[str] = None

class ForeignKeyInfo(BaseModel):
    column: str
    referenced_table: str
    referenced_column: str

class TableSchema(BaseModel):
    table_name: str
    columns: List[ColumnInfo]
    foreign_keys: List[ForeignKeyInfo] = []
    row_count: int = 0

class DatabaseSchema(BaseModel):
    database_type: str = "sqlite"
    tables: Dict[str, TableSchema]

class ValidationResult(BaseModel):
    is_valid: bool
    sanitized_sql: str
    reasons: List[str] = []

class QueryResult(BaseModel):
    natural_query: str
    generated_sql: str
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float
    error: Optional[str] = None

