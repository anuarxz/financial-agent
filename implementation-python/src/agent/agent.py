import json
from pathlib import Path
from typing import Any

from src.agent.client import LLMClient
from src.agent.tools import ToolRegistry
from src.agent.tracer import AgentTracer, TraceType
from src.config import get_settings


class FinancialAgent:
    PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

    def __init__(
        self,
        client: LLMClient,
        tool_registry: ToolRegistry,
        max_iterations: int | None = None,
        tracer: AgentTracer | None = None,
    ):
        self._client = client
        self._tools = tool_registry
        self._max_iterations = max_iterations or get_settings().max_iterations
        self._tracer = tracer or AgentTracer(enabled=True)
        self._system_prompt = self._load_system_prompt()
        self._conversation: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt}
        ]

    def _load_system_prompt(self) -> str:
        prompt_file = self.PROMPTS_DIR / "system_prompt.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return "Eres un asistente financiero inteligente."

    def chat(self, user_message: str) -> str:
        self._tracer.trace(
            TraceType.THINKING,
            "Analizando mensaje del usuario",
            {"entrada": user_message}
        )

        self._conversation.append({"role": "user", "content": user_message})

        for _ in range(self._max_iterations):
            self._tracer.trace(
                TraceType.THINKING,
                "Consultando al modelo LLM para decidir siguiente acción",
                None
            )

            response = self._client.chat_completion(
                messages=self._conversation,
                tools=self._tools.get_tool_definitions(),
            )
            extracted = self._client.extract_response(response)

            tool_calls = extracted.get("tool_calls")
            content = extracted.get("content")
            reasoning_content = extracted.get("reasoning_content")

            if reasoning_content:
                self._tracer.trace(
                    TraceType.THINKING,
                    "Razonamiento interno del modelo",
                    {"pensamiento": reasoning_content}
                )

            if content and tool_calls:
                self._tracer.trace(
                    TraceType.THINKING,
                    "Decisión del modelo",
                    {"razonamiento": content}
                )

            if not tool_calls:
                if content:
                    self._conversation.append({"role": "assistant", "content": content})
                    self._tracer.trace(
                        TraceType.RESPONSE,
                        "Respuesta final del agente",
                        {"respuesta": content}
                    )
                return content or "No estoy seguro de cómo ayudarte con eso."

            tool_names = [tc["function"]["name"] for tc in tool_calls]
            self._tracer.trace(
                TraceType.THINKING,
                "Decisión: usar herramienta(s)",
                {"herramientas_seleccionadas": tool_names}
            )

            assistant_message: dict[str, Any] = {"role": "assistant", "tool_calls": tool_calls}
            if content:
                assistant_message["content"] = content
            self._conversation.append(assistant_message)

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])

                self._tracer.trace(
                    TraceType.TOOL_CALL,
                    f"Ejecutando: {tool_name}",
                    {"parámetros": arguments}
                )

                result = self._tools.execute(tool_name, arguments)

                success = result.get("success", False)
                self._tracer.trace(
                    TraceType.TOOL_RESULT,
                    f"Resultado de {tool_name}: {'éxito' if success else 'error'}",
                    {"datos": result}
                )

                self._conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })

        self._tracer.trace(
            TraceType.ERROR,
            "Máximo de iteraciones alcanzado",
            None
        )
        return "He alcanzado el máximo de operaciones. Por favor, intenta de nuevo."

    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self._conversation = [
            {"role": "system", "content": self._system_prompt}
        ]
        self._tracer.clear()

    def get_traces(self) -> list[dict[str, Any]]:
        """Get all trace entries."""
        return self._tracer.get_traces()
