"""Tool definitions and registry for the agent."""

from typing import Any, Callable

from duckduckgo_search import DDGS

from src.database import FinancialRepository
from src.schemas import TableName


class ToolRegistry:
    """Registro de tools"""

    def __init__(self, repository: FinancialRepository):
        self._repository = repository
        self._tools: dict[str, Callable[..., Any]] = {
            "insert_record": self._insert_record,
            "query_records": self._query_records,
            "web_search": self._web_search,
        }

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "insert_record",
                    "description": (
                        "Insertar un nuevo registro financiero en la base de datos. "
                        "Usar para añadir gastos, ahorros o inversiones."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "enum": ["expenses", "savings", "investments"],
                                "description": "La tabla donde insertar: expenses (gastos), savings (ahorros), investments (inversiones).",
                            },
                            "amount": {
                                "type": "number",
                                "description": "La cantidad monetaria (debe ser positiva).",
                            },
                            "category": {
                                "type": "string",
                                "description": "Para gastos: la categoría (ej: 'comida', 'transporte', 'ocio').",
                            },
                            "goal": {
                                "type": "string",
                                "description": "Para ahorros: el objetivo (ej: 'vacaciones', 'emergencias').",
                            },
                            "asset_type": {
                                "type": "string",
                                "description": "Para inversiones: tipo de activo (ej: 'acciones', 'crypto', 'bonos').",
                            },
                            "description": {
                                "type": "string",
                                "description": "Descripción opcional del registro.",
                            },
                        },
                        "required": ["table", "amount"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "query_records",
                    "description": (
                        "Consultar registros financieros de la base de datos. "
                        "Usar para obtener gastos, ahorros o inversiones guardados."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table": {
                                "type": "string",
                                "enum": ["expenses", "savings", "investments"],
                                "description": "La tabla a consultar.",
                            },
                            "category": {
                                "type": "string",
                                "description": "Filtrar gastos por categoría.",
                            },
                            "goal": {
                                "type": "string",
                                "description": "Filtrar ahorros por objetivo.",
                            },
                            "asset_type": {
                                "type": "string",
                                "description": "Filtrar inversiones por tipo de activo.",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Número máximo de registros a devolver (default 100).",
                            },
                        },
                        "required": ["table"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": (
                        "Buscar información en internet en tiempo real. "
                        "Usar para obtener noticias financieras, cotizaciones, consejos de inversión, "
                        "información sobre mercados, criptomonedas, acciones, etc."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "La consulta de búsqueda (ej: 'precio bitcoin hoy', 'noticias bolsa española').",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Número máximo de resultados (default 5).",
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
        ]

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")

        return tool(**arguments)

    def _insert_record(
        self,
        table: str,
        amount: float,
        category: str | None = None,
        goal: str | None = None,
        asset_type: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        try:
            table_enum = TableName(table)
            data = {
                "amount": amount,
                "category": category,
                "goal": goal,
                "asset_type": asset_type,
                "description": description,
            }
            data = {k: v for k, v in data.items() if v is not None}

            record = self._repository.insert(table_enum, data)
            return {
                "success": True,
                "message": f"Registro insertado correctamente en {table}",
                "record": record,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _query_records(
        self,
        table: str,
        category: str | None = None,
        goal: str | None = None,
        asset_type: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        try:
            table_enum = TableName(table)
            filters = {
                "category": category,
                "goal": goal,
                "asset_type": asset_type,
            }
            filters = {k: v for k, v in filters.items() if v is not None}

            records = self._repository.query(
                table_enum,
                filters=filters if filters else None,
                limit=limit,
            )
            return {
                "success": True,
                "count": len(records),
                "records": records,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _web_search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            formatted_results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in results
            ]

            return {
                "success": True,
                "query": query,
                "count": len(formatted_results),
                "results": formatted_results,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
