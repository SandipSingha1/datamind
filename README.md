# DataMind — AI-Powered Data Intelligence Platform
## Bob-a-thon 2024 Submission

### Quick Start
1. Copy `.env.example` to `.env` and fill in your credentials
2. `pip install -r requirements.txt`
3. `./run.sh`
4. Open http://localhost:8050

### Services
| Service | Port | Purpose |
|---------|------|---------|
| datamind_core | 8001 | FastAPI + LangGraph agents + MCP |
| datamind_knowledge_svc | 8002 | FastAPI + Neo4j + Graph-RAG |
| datamind_frontend | 8050 | Streamlit UI |

### First-time setup
```bash
# 1. Start Neo4j
docker run -d --name neo4j-datamind \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/datamind_pass \
  neo4j:5.15

# 2. Compile dbt (if you have a dbt project)
cd dbt_project && dbt compile && cd ..

# 3. Ingest metadata into Neo4j
cd datamind_knowledge_svc
python ingestion.py ../dbt_project/target/manifest.json

# 4. Start all services
cd .. && ./run.sh
```

### Architecture
- `datamind_core` = booking_system_backend equivalent
- `datamind_knowledge_svc` = booking_system_inventory_hold_service equivalent  
- `datamind_frontend` = booking_system_frontend equivalent

### LangGraph Agents
- **Discovery agent**: finds Snowflake tables/views by keyword
- **Lineage agent**: traverses Neo4j for upstream/downstream paths
- **Generation agent**: writes dbt models via Snowflake Cortex
- **Cost agent**: analyzes QUERY_HISTORY and generates optimization tips

### Bob MCP Registration
Point Bob to: `http://localhost:8001/mcp`
