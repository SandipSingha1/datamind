# DataMind Architecture Documentation

## Overview
DataMind is an AI-powered Data Intelligence Platform that provides intelligent data discovery, lineage tracking, automated dbt model generation, and cost optimization for Snowflake data warehouses. Built for the Bob-a-thon 2026, it leverages IBM's Bob AI assistant through MCP (Model Context Protocol) integration.

---

## System Architecture Diagram

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    Streamlit Frontend (Port 8050)                       │ │
│  │  • Chat Interface with Bob                                              │ │
│  │  • Lineage Explorer (Interactive Visualization)                         │ │
│  │  • Cost Dashboard (Analytics & Charts)                                  │ │
│  │  Tech: Streamlit, Plotly, Pandas, HTTPX                                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP REST API
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CORE ORCHESTRATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │              DataMind Core Service (Port 8001)                          │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    FastAPI Application                            │  │ │
│  │  │  • /chat - Main conversational endpoint                           │  │ │
│  │  │  • /mcp - Bob MCP integration endpoint                            │  │ │
│  │  │  • /cost/summary - Cost analytics                                 │  │ │
│  │  │  • /health - Service health check                                 │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                          │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │ │
│  │  │              LangGraph Workflow Engine                            │  │ │
│  │  │  ┌────────────┐      ┌──────────────────────────────────────┐    │  │ │
│  │  │  │   Router   │─────▶│  Intent Classification               │    │  │ │
│  │  │  │   Node     │      │  • Discovery (find tables)           │    │  │ │
│  │  │  └────────────┘      │  • Lineage (trace dependencies)      │    │  │ │
│  │  │        │             │  • Generation (create dbt models)    │    │  │ │
│  │  │        ▼             │  • Cost (analyze query costs)        │    │  │ │
│  │  │  ┌────────────┐      └──────────────────────────────────────┘    │  │ │
│  │  │  │  Enrich    │                                                   │  │ │
│  │  │  │   Node     │◀──── Fetches Graph Context from Knowledge Svc    │  │ │
│  │  │  └────────────┘                                                   │  │ │
│  │  │        │                                                           │  │ │
│  │  │        ▼                                                           │  │ │
│  │  │  ┌──────────────────────────────────────────────────────────┐    │  │ │
│  │  │  │           Specialized Agent Nodes                        │    │  │ │
│  │  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │  │ │
│  │  │  │  │  Discovery   │  │   Lineage    │  │ Generation   │   │    │  │ │
│  │  │  │  │    Agent     │  │    Agent     │  │    Agent     │   │    │  │ │
│  │  │  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │  │ │
│  │  │  │  ┌──────────────┐                                        │    │  │ │
│  │  │  │  │     Cost     │                                        │    │  │ │
│  │  │  │  │    Agent     │                                        │    │  │ │
│  │  │  │  └──────────────┘                                        │    │  │ │
│  │  │  └──────────────────────────────────────────────────────────┘    │  │ │
│  │  │                                                                   │  │ │
│  │  │  Tech: LangGraph, LangChain, Pydantic, Langfuse (Observability) │  │ │
│  │  └──────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
           │                                    │
           │ Snowflake                          │ HTTP REST API
           │ Connector                          │
           ▼                                    ▼
┌──────────────────────────┐    ┌────────────────────────────────────────────┐
│   EXTERNAL DATA LAYER    │    │      KNOWLEDGE GRAPH LAYER                 │
│  ┌────────────────────┐  │    │  ┌──────────────────────────────────────┐ │
│  │    Snowflake       │  │    │  │  Knowledge Service (Port 8002)       │ │
│  │  Data Warehouse    │  │    │  │  ┌────────────────────────────────┐  │ │
│  │                    │  │    │  │  │      FastAPI Application       │  │ │
│  │  • Tables/Views    │  │    │  │  │  • /rag/context - Graph-RAG    │  │ │
│  │  • Query History   │  │    │  │  │  • /lineage/explain - Lineage  │  │ │
│  │  • Metadata        │  │    │  │  │  • /health - Health check      │  │ │
│  │  • Cortex AI       │  │    │  │  └────────────────────────────────┘  │ │
│  │    (LLM)           │  │    │  │                                        │ │
│  └────────────────────┘  │    │  │  ┌────────────────────────────────┐  │ │
│                          │    │  │  │      Graph-RAG Engine          │  │ │
│  Tech: Snowflake         │    │  │  │  • Entity Context Retrieval    │  │ │
│  Connector Python,       │    │  │  │  • Lineage Path Traversal      │  │ │
│  Snowflake Cortex        │    │  │  │  • Cypher Query Generation     │  │ │
└──────────────────────────┘    │  │  └────────────────────────────────┘  │ │
                                │  │            │                          │ │
                                │  │            ▼                          │ │
                                │  │  ┌────────────────────────────────┐  │ │
                                │  │  │      Neo4j Graph Database      │  │ │
                                │  │  │  • Data Lineage Graph          │  │ │
                                │  │  │  • dbt Model Relationships     │  │ │
                                │  │  │  • Table Dependencies          │  │ │
                                │  │  │  • Metadata Properties         │  │ │
                                │  │  │  Tech: Neo4j 5.15, APOC        │  │ │
                                │  │  └────────────────────────────────┘  │ │
                                │  │                                        │ │
                                │  │  Tech: Neo4j Driver, LangChain-Neo4j  │ │
                                │  └──────────────────────────────────────┘ │
                                └────────────────────────────────────────────┘
                                                 ▲
                                                 │ Metadata Ingestion
                                                 │
                                    ┌────────────────────────────┐
                                    │   dbt Project              │
                                    │  • manifest.json           │
                                    │  • Models (SQL)            │
                                    │  • Sources                 │
                                    │  • Tests                   │
                                    │  Tech: dbt-core, dbt-snowflake │
                                    └────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         OBSERVABILITY & INTEGRATION                          │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    Langfuse Observability                               │ │
│  │  • Trace all agent executions                                           │ │
│  │  • Monitor LLM calls and costs                                          │ │
│  │  • Debug workflow paths                                                 │ │
│  │  Tech: Langfuse SDK, @observe decorators                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    Bob MCP Integration                                  │ │
│  │  • Streamable HTTP MCP Server                                           │ │
│  │  • ask_datamind tool exposed to Bob                                     │ │
│  │  • JSON-RPC 2.0 protocol                                                │ │
│  │  Tech: MCP Protocol 2024-11-05                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend Layer (Streamlit - Port 8050)

**Technology Stack:**
- **Streamlit**: Web application framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **HTTPX**: Async HTTP client for API calls

**Features:**
- **Chat Interface**: Natural language interaction with Bob
- **Lineage Explorer**: Visual data lineage with network graphs
- **Cost Dashboard**: Query cost analytics with daily breakdowns
- **Service Health Monitoring**: Real-time status of backend services

**Key Files:**
- `datamind_frontend/app_streamlit.py` - Main application

---

### 2. Core Orchestration Layer (FastAPI + LangGraph - Port 8001)

**Technology Stack:**
- **FastAPI**: High-performance async web framework
- **LangGraph**: Workflow orchestration for AI agents
- **LangChain**: LLM integration and tooling
- **Pydantic**: Data validation and settings management
- **Langfuse**: Observability and tracing
- **Uvicorn**: ASGI server

**Components:**

#### A. FastAPI Application (`main.py`)
**Endpoints:**
- `POST /chat` - Main conversational endpoint
  - Accepts user queries
  - Routes through LangGraph workflow
  - Returns structured responses with intent classification
  
- `POST /mcp` - Bob MCP integration
  - Implements JSON-RPC 2.0 protocol
  - Exposes `ask_datamind` tool to Bob
  - Handles initialize, tools/list, tools/call methods
  
- `GET /cost/summary` - Cost analytics
  - Aggregates Snowflake query costs
  - Returns daily breakdowns
  
- `GET /health` - Health check endpoint

#### B. LangGraph Workflow (`graph/workflow.py`)

**Workflow Nodes:**

1. **Router Node** (`graph/router.py`)
   - Analyzes user query using keyword matching
   - Classifies intent: DISCOVERY, LINEAGE, GENERATION, or COST
   - Extracts entity names (table names, model names) using regex
   - Returns: intent classification + extracted entities

2. **Enrich Node** (`graph/workflow.py`)
   - Calls Knowledge Service for graph context
   - Retrieves Neo4j neighborhood data for entities
   - Enriches state with relevant metadata
   - Returns: graph context string

3. **Agent Nodes** (Specialized handlers)

   **Discovery Agent** (`graph/agents/discovery.py`)
   - Searches Snowflake INFORMATION_SCHEMA
   - Finds tables/views matching keywords
   - Uses Snowflake Cortex AI for natural language response
   - Returns: list of matching assets + AI-generated answer

   **Lineage Agent** (`graph/agents/lineage.py`)
   - Calls Knowledge Service lineage API
   - Traverses Neo4j graph for dependencies
   - Explains upstream/downstream relationships
   - Returns: lineage paths + AI explanation

   **Generation Agent** (`graph/agents/generation.py`)
   - Generates dbt SQL models using Snowflake Cortex
   - Uses available table list as context
   - Creates production-ready SQL with CTEs
   - Returns: model name + SQL code

   **Cost Agent** (`graph/agents/cost.py`)
   - Queries SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
   - Analyzes top expensive queries (last 7 days)
   - Uses Cortex AI for optimization recommendations
   - Returns: cost data + optimization tips

**State Management:**
- Uses TypedDict for type-safe state passing
- State includes: user_query, intent, entities, results, answer, trace_id
- Each node updates state immutably

**Key Files:**
- `main.py` - FastAPI application
- `graph/workflow.py` - LangGraph workflow definition
- `graph/router.py` - Intent classification
- `graph/state.py` - State schema
- `graph/agents/*.py` - Specialized agent implementations
- `tools/snowflake_tool.py` - Snowflake integration tools

---

### 3. Knowledge Graph Layer (FastAPI + Neo4j - Port 8002)

**Technology Stack:**
- **FastAPI**: Web framework
- **Neo4j 5.15**: Graph database
- **Neo4j Python Driver**: Database connectivity
- **LangChain-Neo4j**: Graph integration utilities
- **APOC**: Neo4j procedures library

**Components:**

#### A. FastAPI Application (`main.py`)
**Endpoints:**
- `POST /rag/context` - Graph-RAG context retrieval
  - Input: list of entity names + query
  - Returns: enriched context from Neo4j graph
  
- `POST /lineage/explain` - Lineage path traversal
  - Input: asset name, direction (upstream/downstream/both), depth
  - Returns: all paths with relationships

#### B. Graph-RAG Engine (`graph_rag.py`)

**Functions:**

1. **get_graph_context()**
   - For each entity, queries Neo4j for immediate neighbors
   - Retrieves node properties (type, description, row count)
   - Formats as plain text for LLM consumption
   - Returns: context string with relationships

2. **explain_lineage()**
   - Executes Cypher queries for path traversal
   - Supports upstream, downstream, or bidirectional
   - Limits depth to prevent graph explosion
   - Returns: structured paths with node chains and relationships

#### C. Neo4j Database

**Graph Schema:**
- **Nodes**: 
  - `DbtModel` - dbt models from manifest.json
  - `SnowflakeTable` - Physical Snowflake tables
  - `DbtSource` - Source definitions
  
- **Relationships**:
  - `DEPENDS_ON` - Model dependencies
  - `READS_FROM` - Source table reads
  - `WRITES_TO` - Output table writes

**Properties:**
- name, description, materialization, row_count, schema, database

#### D. Metadata Ingestion (`ingestion.py`)
- Parses dbt manifest.json
- Creates nodes and relationships in Neo4j
- Establishes lineage graph
- Run once after dbt compile

**Key Files:**
- `datamind_knowledge_svc/main.py` - FastAPI app
- `datamind_knowledge_svc/graph_rag.py` - Graph-RAG logic
- `datamind_knowledge_svc/neo4j_client.py` - Neo4j connection
- `datamind_knowledge_svc/ingestion.py` - Metadata loader

---

### 4. External Data Layer (Snowflake)

**Technology Stack:**
- **Snowflake Connector Python**: Database connectivity
- **Snowflake Cortex**: Built-in LLM capabilities
- **Snowflake SQLAlchemy**: ORM support

**Integration Points:**

1. **Metadata Discovery**
   - INFORMATION_SCHEMA.TABLES
   - INFORMATION_SCHEMA.COLUMNS
   - Table comments and descriptions

2. **Query Cost Analysis**
   - SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
   - Execution time, credits used
   - User attribution

3. **AI Capabilities**
   - SNOWFLAKE.CORTEX.COMPLETE() - LLM completions
   - Used for natural language generation
   - Model: snowflake-arctic (configurable)

**Key Files:**
- `tools/snowflake_tool.py` - Snowflake tools and utilities
- `.env` - Snowflake credentials (SF_ACCOUNT, SF_USER, etc.)

---

### 5. dbt Integration

**Technology Stack:**
- **dbt-core**: Transformation framework
- **dbt-snowflake**: Snowflake adapter

**Components:**
- `dbt_project/` - dbt project directory
- `models/` - SQL transformation models
- `target/manifest.json` - Compiled metadata (ingested to Neo4j)

**Workflow:**
1. Developer writes dbt models
2. `dbt compile` generates manifest.json
3. Ingestion script loads metadata to Neo4j
4. DataMind can now trace lineage and generate new models

---

## Data Flow Examples

### Example 1: Discovery Query
```
User: "Find tables related to orders"
  ↓
Frontend (Streamlit) → POST /chat
  ↓
Core Service (FastAPI)
  ↓
LangGraph Workflow:
  1. Router Node → Intent: DISCOVERY, Entities: ["orders"]
  2. Enrich Node → Fetch graph context from Knowledge Service
  3. Discovery Agent → Query Snowflake INFORMATION_SCHEMA
                    → Use Cortex AI for natural language response
  ↓
Response: "Found 3 tables: orders, order_items, order_status..."
  ↓
Frontend displays results
```

### Example 2: Lineage Query
```
User: "Show lineage for fct_orders"
  ↓
Frontend → POST /chat
  ↓
Core Service
  ↓
LangGraph Workflow:
  1. Router Node → Intent: LINEAGE, Entities: ["fct_orders"]
  2. Enrich Node → Fetch graph context
  3. Lineage Agent → POST /lineage/explain to Knowledge Service
                   → Neo4j Cypher query for paths
                   → Use Cortex AI to explain lineage
  ↓
Response: "fct_orders depends on stg_orders and stg_customers..."
  ↓
Frontend displays lineage paths
```

### Example 3: dbt Model Generation
```
User: "Generate monthly revenue dbt model"
  ↓
Frontend → POST /chat
  ↓
Core Service
  ↓
LangGraph Workflow:
  1. Router Node → Intent: GENERATION
  2. Enrich Node → Fetch available tables
  3. Generation Agent → Query Snowflake for table list
                     → Use Cortex AI to generate SQL
                     → Format as dbt model
  ↓
Response: SQL code with model name and file path
  ↓
Frontend displays code with syntax highlighting
```

### Example 4: Cost Analysis
```
User: "Which queries cost the most?"
  ↓
Frontend → POST /chat
  ↓
Core Service
  ↓
LangGraph Workflow:
  1. Router Node → Intent: COST
  2. Enrich Node → (skipped for cost queries)
  3. Cost Agent → Query ACCOUNT_USAGE.QUERY_HISTORY
                → Use Cortex AI for optimization tips
  ↓
Response: Top 5 expensive queries + recommendations
  ↓
Frontend displays cost breakdown
```

---

## Technology Stack Summary

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Streamlit, Plotly, Pandas, HTTPX |
| **Core Backend** | FastAPI, LangGraph, LangChain, Pydantic, Uvicorn |
| **Knowledge Service** | FastAPI, Neo4j, Neo4j Python Driver, LangChain-Neo4j |
| **Database** | Neo4j 5.15 (Graph), Snowflake (Data Warehouse) |
| **AI/LLM** | Snowflake Cortex (snowflake-arctic model) |
| **Observability** | Langfuse (tracing and monitoring) |
| **Integration** | MCP Protocol (Bob integration), JSON-RPC 2.0 |
| **Data Transformation** | dbt-core, dbt-snowflake |
| **Containerization** | Docker, Docker Compose |

---

## Deployment Architecture

### Docker Compose Services

```yaml
services:
  neo4j:           # Port 7474 (UI), 7687 (Bolt)
  knowledge_svc:   # Port 8002
  core:            # Port 8001
  frontend:        # Port 8050
```

**Service Dependencies:**
- frontend → core → knowledge_svc → neo4j
- core → snowflake (external)

**Environment Variables:**
- Snowflake credentials (SF_ACCOUNT, SF_USER, SF_PASSWORD, etc.)
- Neo4j credentials (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
- Service URLs (CORE_URL, KNOWLEDGE_SVC_URL)
- Cortex model selection (CORTEX_MODEL)

---

## Key Design Patterns

### 1. Microservices Architecture
- Separation of concerns: UI, orchestration, knowledge graph
- Independent scaling and deployment
- Service-to-service communication via REST APIs

### 2. Agent-Based Architecture (LangGraph)
- Specialized agents for different intents
- State-based workflow orchestration
- Conditional routing based on intent classification

### 3. Graph-RAG Pattern
- Knowledge graph as context source
- Entity-centric retrieval
- Enriches LLM prompts with structured data

### 4. Observability-First Design
- All agent executions traced with Langfuse
- @observe decorators on critical functions
- Trace IDs for request tracking

### 5. MCP Integration Pattern
- Exposes DataMind as a tool to Bob
- Standardized protocol for AI assistant integration
- Bidirectional communication

---

## Security Considerations

1. **Credentials Management**
   - Environment variables for sensitive data
   - No hardcoded credentials
   - .env file excluded from version control

2. **API Security**
   - CORS middleware configured
   - Input validation with Pydantic
   - Error handling and sanitization

3. **Database Security**
   - Neo4j authentication required
   - Snowflake role-based access control
   - Parameterized queries to prevent injection

---

## Performance Optimizations

1. **Async Operations**
   - FastAPI async endpoints
   - asyncio.to_thread for blocking operations
   - HTTPX async client

2. **Caching Strategy**
   - Neo4j query result caching (implicit)
   - Session state management in frontend

3. **Query Optimization**
   - Limited result sets (LIMIT clauses)
   - Indexed Neo4j properties
   - Efficient Cypher queries

4. **Resource Management**
   - Connection pooling for Snowflake
   - Neo4j driver connection management
   - Docker resource limits

---

## Monitoring and Debugging

### Langfuse Observability
- **Traces**: Full execution path of each request
- **Spans**: Individual agent and tool executions
- **Metrics**: LLM token usage, latency, costs
- **Debugging**: Step-by-step workflow visualization

### Health Checks
- `/health` endpoints on all services
- Frontend service status indicators
- Docker container health checks

### Logging
- Structured logging in all services
- Error traceback capture
- Request/response logging

---

## Future Enhancements

1. **Advanced Analytics**
   - Predictive cost modeling
   - Anomaly detection in query patterns
   - Usage trend analysis

2. **Enhanced Lineage**
   - Column-level lineage
   - Impact analysis for schema changes
   - Automated data quality checks

3. **Collaboration Features**
   - Shared sessions
   - Annotation and comments
   - Team workspaces

4. **Extended Integrations**
   - Additional data sources (BigQuery, Databricks)
   - CI/CD pipeline integration
   - Slack/Teams notifications

---

## Conclusion

DataMind demonstrates a modern, AI-powered approach to data intelligence by combining:
- **Graph databases** for relationship modeling
- **LLM capabilities** for natural language interaction
- **Workflow orchestration** for complex agent coordination
- **Observability** for production-grade monitoring
- **MCP integration** for seamless Bob assistant connectivity

The architecture is designed for scalability, maintainability, and extensibility, making it suitable for enterprise data platforms.

---

## Quick Reference

### Start All Services
```bash
docker-compose up -d
```

### Access Points
- Frontend: http://localhost:8050
- Core API: http://localhost:8001
- Knowledge API: http://localhost:8002
- Neo4j Browser: http://localhost:7474

### Bob MCP Configuration
```json
{
  "mcpServers": {
    "datamind": {
      "url": "http://localhost:8001/mcp",
      "transport": "streamable-http"
    }
  }
}
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-23  
**Author**: DataMind Team (Bob-a-thon 2026)