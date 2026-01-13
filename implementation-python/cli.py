"""Interactive CLI for the Financial Agent."""

import sys

from src.agent import FinancialAgent, LLMClient, ToolRegistry
from src.database import DatabaseConnection, FinancialRepository
from src.config import get_settings


def create_agent() -> FinancialAgent:
    """Create and configure the financial agent."""
    db_connection = DatabaseConnection()
    db_connection.initialize_schema()
    repository = FinancialRepository(db_connection)
    client = LLMClient()
    tool_registry = ToolRegistry(repository)

    return FinancialAgent(client=client, tool_registry=tool_registry)


def print_banner() -> None:
    settings = get_settings()
    print("\n" + "=" * 60)
    print("  FINANCIAL AGENT - Asistente Financiero Inteligente")


def main() -> None:
    """Run the interactive CLI."""
    print_banner()

    try:
        agent = create_agent()
        print("Agente inicializado correctamente\n")
    except Exception as e:
        print(f"Error inicializando el agente: {e}")
        sys.exit(1)

    while True:
        try:
            user_input = input("\n - Tú: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("salir", "exit", "quit"):
                print("\n¡Hasta luego!")
                break

            if user_input.lower() == "reset":
                agent.reset_conversation()
                print("Conversación reiniciada.")
                continue

            if user_input.lower() == "help":
                print_banner()
                continue

            print()  
            response = agent.chat(user_input)
            print(f"\n🤖 Asistente: {response}")

        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
