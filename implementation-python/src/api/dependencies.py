from functools import lru_cache

from src.agent import FinancialAgent, LLMClient, ToolRegistry
from src.database import DatabaseConnection, FinancialRepository


@lru_cache
def get_db_connection() -> DatabaseConnection:
    return DatabaseConnection()


@lru_cache
def get_agent() -> FinancialAgent:
    db_connection = get_db_connection()
    repository = FinancialRepository(db_connection)
    client = LLMClient()
    tool_registry = ToolRegistry(repository)

    return FinancialAgent(client=client, tool_registry=tool_registry)
