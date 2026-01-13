# Financial Agent

Agente inteligente de IA para gestión de finanzas personales con capacidad de razonamiento y uso de tools.

## Tools disponibles:
  - `insert_record`: Insertar gastos, ahorros e inversiones en PostgreSQL
  - `query_records`: Consultar registros de la base de datos
  - `web_search`: Búsqueda en tiempo real (noticias, cotizaciones, información financiera)

- Trazabilidad (Chain of Thought): Muestra el proceso de razonamiento del agente
- Multi-provider LLM: Soporta Gemini, OpenAI, Anthropic, Groq, OpenRouter via LiteLLM
- Dos modos de interacción: CLI interactivo y API REST


## Inicialización

# Linux/Mac:
make docker-cli    # CLI interactivo
make docker-api    # API REST (http://localhost:8000)

# Windows (PowerShell):
.\make.bat docker-cli    # CLI interactivo
.\make.bat docker-api    # API REST (http://localhost:8000)

Nota Windows: En PowerShell usar `.\make.bat <comando>`, en CMD usar `make.bat <comando>`


## API Endpoints

| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/chat` | Enviar mensaje al agente |
| POST | `/api/v1/chat/reset` | Reiniciar conversación |
| GET | `/api/v1/traces` | Ver trazas de razonamiento |


## Trazabilidad 

El agente muestra su proceso de razonamiento con:

- THINKING: Análisis y decisiones del agente
- TOOL_CALL: Herramienta que decide usar y argumentos
- TOOL_RESULT: Resultado de la ejecución
- RESPONSE: Respuesta final al usuario
- ERROR: Errores durante el proceso


## Base de Datos

### Gastos (expenses)
- id
- amount
- category
- description
- created_at

### Ahorros (savings)
- id
- amount
- goal
- description
- created_at

### Inversiones (investments)
- id
- amount
- asset_type
- description
- created_at

