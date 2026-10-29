from src.executor import SafeSQLExecutor
from src.server import SafeSQLServerHandler

DB_PATH = "fixtures/chinook.db"

def test_server_handler_init():
    exec = SafeSQLExecutor(DB_PATH)
    SafeSQLServerHandler.executor = exec
    assert SafeSQLServerHandler.executor is not None

