# Financial Agent - n8n 

Implementación del agente financiero usando n8n

## Inicio 

```bash
docker-compose up -d
```

Esto inicia:
- PostgreSQL en puerto `5433`
- PostgREST en puerto `3000` (API REST para PostgreSQL)
- n8n en puerto `5678`

### 3. Acceder a n8n

http://localhost:5678

### 4. Configurar credenciales en n8n

#### PostgreSQL
   - Host: `db`
   - Database: `financial_agent`
   - User: `postgres`
   - Password: `postgres`
   - Port: `5432`

#### Google Gemini en Credenciales

### 5. Importar workflows

   1. `workflow-tool-insert.json` - Herramienta para insertar registros
   2. `workflow-tool-query.json` - Herramienta para consultar registros
   3. `workflow-tool-search.json` - Herramienta para búsqueda web (DuckDuckGo)
   4. `workflow.json` - Workflow principal del agente

Conectar los sub-workflows como tools

### 6. Activar el workflow

## Uso

```bash
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Añade un gasto de 50 euros en comida"}'
```
