"""Tracer for Chain of Thought logging."""

import json
from datetime import datetime
from enum import Enum
from typing import Any


class TraceType(str, Enum):
    THINKING = "THINKING"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"


class AgentTracer:
    """Traces and logs agent's chain of thought."""

    COLORS = {
        TraceType.THINKING: "\033[94m",     # Blue
        TraceType.TOOL_CALL: "\033[93m",    # Yellow
        TraceType.TOOL_RESULT: "\033[92m",  # Green
        TraceType.RESPONSE: "\033[95m",     # Magenta
        TraceType.ERROR: "\033[91m",        # Red
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._traces: list[dict[str, Any]] = []

    def trace(self, trace_type: TraceType, message: str, data: dict[str, Any] | None = None) -> None:
        timestamp = datetime.now().isoformat()
        trace_entry = {
            "timestamp": timestamp,
            "type": trace_type.value,
            "message": message,
            "data": data,
        }
        self._traces.append(trace_entry)

        if self._enabled:
            self._print_trace(trace_type, message, data)

    def _print_trace(self, trace_type: TraceType, message: str, data: dict[str, Any] | None) -> None:
        color = self.COLORS.get(trace_type, "")

        print(f"\n{color}{'─'*60}")
        print(f"{self.BOLD}[{trace_type.value}]{self.RESET}{color} {message}")

        if data:
            for key, value in data.items():
                formatted_value = self._format_value(value)
                print(f"  └─ {key}: {formatted_value}")

        print(f"{'─'*60}{self.RESET}")

    def _format_value(self, value: Any) -> str:
        if isinstance(value, dict):
            # Pretty print dicts
            formatted = json.dumps(value, ensure_ascii=False, indent=2)
            if len(formatted) > 300:
                formatted = formatted[:300] + "..."
            # Indent multiline
            lines = formatted.split('\n')
            if len(lines) > 1:
                return '\n      ' + '\n      '.join(lines)
            return formatted
        elif isinstance(value, list):
            return str(value)
        elif isinstance(value, str):
            if len(value) > 200:
                return value[:200] + "..."
            return value
        return str(value)

    def get_traces(self) -> list[dict[str, Any]]:
        return self._traces.copy()

    def clear(self) -> None:
        self._traces.clear()
