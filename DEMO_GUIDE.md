# DataMind - 3-Minute Demo Guide

**Simple, Clear, Judge-Ready**

---

## 🎯 What is DataMind?

**DataMind gives IBM Bob a working memory of your entire data platform.**

It's an AI assistant that understands your Snowflake data warehouse, dbt models, and data lineage through a Neo4j knowledge graph.

---

## 🏗️ Technology Stack

| Technology | Purpose | What It Does |
|------------|---------|--------------|
| **Snowflake** | Data Warehouse | Stores your business data (orders, customers, products) |
| **dbt** | Data Transformation | Transforms raw data into analytics-ready models |
| **Neo4j** | Knowledge Graph | Stores metadata and lineage relationships |
| **LangGraph** | Agent Orchestration | Routes queries to specialized AI agents |
| **LangChain** | Tool Integration | Connects agents to Snowflake and Neo4j |
| **LangFuse** | Observability | Traces every AI decision and LLM call |
| **LangSmith** | Monitoring | Automatic LangChain/LangGraph tracing |
| **Streamlit** | User Interface | Chat UI, lineage visualizer, cost dashboard |
| **FastAPI** | Backend Services | REST APIs and MCP endpoint for Bob |

---

## 💼 Use Cases

### 1. **Data Discovery**
**Problem:** "I need to find tables related to customer orders"  
**Solution:** Discovery agent searches Snowflake metadata and explains what's available

### 2. **Lineage Tracing**
**Problem:** "Why did my revenue metric break?"  
**Solution:** Lineage agent traces upstream dependencies through Neo4j graph

### 3. **Code Generation**
**Problem:** "I need a dbt model for monthly revenue by region"  
**Solution:** Generation agent writes production-ready SQL using Snowflake Cortex

### 4. **Cost Optimization**
**Problem:** "Which queries are costing us the most?"  
**Solution:** Cost agent analyzes query history and suggests optimizations

---

## 🎬 Demo Script (3 Minutes)

### **Setup (Before Demo - 10 minutes before judging)**

**IMPORTANT:** All services must be running BEFORE you start the demo!

1. **Start all 3 services** (see "How to Run DataMind" section below):
   ```bash
   # Terminal 1
   cd datamind/datamind_knowledge_svc
   uvicorn main:app --port 8002 --reload
   
   # Terminal 2
   cd datamind/datamind_core
   uvicorn main:app --port 8001 --reload
   
   # Terminal 3
   cd datamind/datamind_frontend
   streamlit run app_streamlit.py
   ```

2. **Verify services are running:**
   - Streamlit UI opens automatically at http://localhost:8050
   - Test with one query: "Find tables related to orders"
   - Confirm you get a response

3. **Open monitoring tools:**
   - LangFuse dashboard on phone: https://cloud.langfuse.com
   - Neo4j Browser in background tab: http://localhost:7474

4. **Warm up the system:**
   - Send 1-2 test queries to load models into memory
   - This prevents slow first-query delays during demo

---

### **Minute 1: Discovery (30 seconds)**

**SAY:** "DataMind helps you discover data assets using natural language."

**DO:**
1. Click **"Chat with Bob"** page (already open)
2. Type: `Find tables related to orders`
3. Press Send

**SHOW:**
- Streamlit displays matching tables with row counts
- Open LangFuse on phone
- Point to trace tree: router → discovery agent → Snowflake query → Cortex LLM

**SAY:** "Every step is traced - intent classification, database query, AI reasoning."

---

### **Minute 2: Lineage (45 seconds)**

**SAY:** "Now let's visualize data lineage to understand dependencies."

**DO:**
1. Click **"Lineage Explorer"** page
2. Type asset name: `fct_orders`
3. Select direction: `both`
4. Click **"Explore"**

**SHOW:**
- Graph visualization appears
- Blue nodes = dbt models
- Teal nodes = Snowflake tables
- Arrows show dependencies

**SAY:** "This is live from Neo4j. If a table breaks, we instantly see what's affected."

**BONUS:** Switch to Neo4j Browser tab, run:
```cypher
MATCH (m:DbtModel)-[:DEPENDS_ON]->(d) RETURN m, d LIMIT 10
```
Show the same graph in Neo4j.

---

### **Minute 3: Generation (45 seconds)**

**SAY:** "DataMind can generate production-ready dbt models."

**DO:**
1. Click **"Chat with Bob"** page
2. Type: `Generate a dbt model for monthly revenue by customer segment`
3. Press Send

**SHOW:**
- Complete SQL code appears
- Proper CTEs, ref() functions, clean formatting
- Open LangFuse trace
- Show generation agent → table discovery → Cortex code generation

**SAY:** "Cortex writes the SQL. LangFuse shows every reasoning step. This is explainable AI."

---

### **Bonus: Cost Dashboard (30 seconds if time)**

**DO:**
1. Click **"Cost Dashboard"** page

**SHOW:**
- Top expensive queries
- Daily cost breakdown chart
- Total spend metrics

**SAY:** "Real-time cost visibility from Snowflake query history."

---

## 📱 Streamlit Pages Explained

### **Page 1: Chat with Bob**
- **What:** Natural language interface to DataMind
- **How:** Type questions, get AI answers
- **Shows:** Discovery, lineage explanations, generated code, cost analysis
- **Try:** "Find tables related to customers", "Show lineage for fct_orders"

### **Page 2: Lineage Explorer**
- **What:** Visual graph of data dependencies
- **How:** Enter table/model name, select direction, click Explore
- **Shows:** Interactive network diagram from Neo4j
- **Try:** Asset name: `fct_orders`, Direction: `both`

### **Page 3: Cost Dashboard**
- **What:** Snowflake query cost analytics
- **How:** Automatically loads last 7 days
- **Shows:** Top expensive queries, daily costs, optimization tips
- **Try:** Just open the page - data loads automatically

---

## 🎯 Key Demo Points

### **What Makes DataMind Special?**

1. **Knowledge Graph** - Neo4j stores relationships, not just data
2. **Multi-Agent** - Specialized agents for different tasks
3. **Full Observability** - Every decision traced in LangFuse
4. **Production-Ready** - Real Snowflake, real dbt, real lineage

### **Technical Highlights**

- ✅ LangGraph orchestrates 4 specialized agents
- ✅ LangFuse traces every LLM call and tool invocation
- ✅ Neo4j provides graph-based context (Graph-RAG)
- ✅ Snowflake Cortex generates code and answers
- ✅ MCP protocol connects to IBM Bob

---

## 🗣️ Talking Points

**For Judges:**
- "This isn't just a chatbot - it's a multi-agent system with memory"
- "The knowledge graph makes answers more accurate than generic LLMs"
- "Full observability means we can debug and improve the AI"
- "It works with real enterprise tools - Snowflake, dbt, Neo4j"

**For Technical Audience:**
- "LangGraph handles agent routing and state management"
- "Graph-RAG enriches prompts with Neo4j context"
- "LangFuse gives us production-grade observability"
- "MCP protocol makes it Bob-compatible"

---

## ⚡ Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| Services not responding | Check all 3 terminals are running |
| No traces in LangFuse | Verify API keys in .env, restart services |
| Empty lineage graph | Run ingestion: `python ingestion.py` |
| Streamlit error | Restart: `streamlit run app_streamlit.py` |

---

## 🚀 How to Run DataMind (Step-by-Step)

### **Prerequisites**
Before starting, ensure you have:
- Python 3.10+ installed
- Neo4j running (Docker or AuraDB)
- Snowflake account with credentials
- LangFuse account (free at cloud.langfuse.com)
- LangSmith account (free at smith.langchain.com)

---

### **Step 1: Install Dependencies** (5 minutes)

Open terminal in the `datamind` directory:

```bash
# Install all Python packages
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, langfuse, langgraph; print('✓ All packages installed')"
```

---

### **Step 2: Configure Environment** (3 minutes)

Edit the `.env` file with your credentials:

```bash
# Open .env file
notepad .env   # Windows
nano .env      # Mac/Linux
```

**Required settings:**
```env
# Snowflake (get from your admin)
SF_ACCOUNT=yourorg.snowflakecomputing.com
SF_USER=your_username
SF_PASSWORD=your_password
SF_WAREHOUSE=COMPUTE_WH
SF_DATABASE=DATAMIND_DB
SF_SCHEMA=PUBLIC

# Neo4j (use these if running Docker)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=datamind_pass

# LangFuse (get from cloud.langfuse.com)
LANGFUSE_PUBLIC_KEY=pk-lf-your-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-key-here

# LangSmith (get from smith.langchain.com)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your-key-here
```

Save and close the file.

---

### **Step 3: Start Neo4j** (2 minutes)

**Option A: Docker (Recommended)**
```bash
docker run -d --name neo4j-datamind \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/datamind_pass \
  neo4j:5.15

# Wait 10 seconds for Neo4j to start
timeout 10  # Windows: timeout /t 10
```

**Option B: AuraDB (Cloud)**
- Already running, just use the URI from your AuraDB console

**Verify Neo4j is running:**
```bash
# Open Neo4j Browser
# Windows: start http://localhost:7474
# Mac: open http://localhost:7474
# Linux: xdg-open http://localhost:7474
```

---

### **Step 4: Load Data into Neo4j** (3 minutes)

```bash
# Terminal 1: Navigate to knowledge service
cd datamind_knowledge_svc

# Run ingestion script
python ingestion.py

# You should see:
# ✓ Neo4j constraints and indexes created
# ✓ Tables ingested
# ✓ Columns ingested
# ✓ dbt manifest ingested
# ✓ Ingestion complete!
```

---

### **Step 5: Start All Services** (2 minutes)

Open **3 separate terminal windows/tabs**:

**Terminal 1 - Knowledge Service (Port 8002):**
```bash
cd datamind/datamind_knowledge_svc
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Wait for: "Application startup complete"
```

**Terminal 2 - Core Service (Port 8001):**
```bash
cd datamind/datamind_core
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Wait for: "Application startup complete"
```

**Terminal 3 - Streamlit Frontend (Port 8050):**
```bash
cd datamind/datamind_frontend
streamlit run app_streamlit.py

# Wait for: "You can now view your Streamlit app in your browser"
# Browser should auto-open to http://localhost:8050
```

---

### **Step 6: Verify Everything Works** (2 minutes)

**Test 1: Check service health**
```bash
# Open new terminal
curl http://localhost:8001/health
curl http://localhost:8002/health

# Both should return: {"status":"ok"}
```

**Test 2: Send a test query**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Find tables related to orders"}'

# Should return JSON with answer and intent
```

**Test 3: Open Streamlit**
- Browser should show DataMind at http://localhost:8050
- Try typing: "Find tables related to orders"
- Should get a response within 5-10 seconds

**Test 4: Check LangFuse traces**
- Open https://cloud.langfuse.com
- Go to your project
- You should see traces from the test query

---

### **Step 7: You're Ready!** ✅

All services are running. You can now:
- Chat with DataMind at http://localhost:8050
- View API docs at http://localhost:8001/docs
- Check Neo4j at http://localhost:7474
- Monitor traces at https://cloud.langfuse.com

---

## 🔄 Quick Start/Stop Commands

**Start everything:**
```bash
# Terminal 1
cd datamind/datamind_knowledge_svc && uvicorn main:app --port 8002 --reload

# Terminal 2
cd datamind/datamind_core && uvicorn main:app --port 8001 --reload

# Terminal 3
cd datamind/datamind_frontend && streamlit run app_streamlit.py
```

**Stop everything:**
- Press `Ctrl+C` in each terminal window
- Or close all terminal windows

**Restart after changes:**
- Services auto-reload when you edit Python files
- Streamlit auto-reloads when you edit app_streamlit.py

---

## 📋 Pre-Demo Checklist

- [ ] All 3 services running (8001, 8002, 8050)
- [ ] LangFuse API keys configured in .env
- [ ] LangSmith API key configured in .env
- [ ] Neo4j running with data (check http://localhost:7474)
- [ ] Streamlit opens at localhost:8050
- [ ] Test query works: "Find tables related to orders"
- [ ] LangFuse dashboard open on phone (cloud.langfuse.com)
- [ ] Practice demo 2-3 times

---

## 🎓 Demo Flow Summary

```
1. DISCOVERY (30s)
   Chat → "Find tables related to orders" → Show trace

2. LINEAGE (45s)
   Lineage Explorer → "fct_orders" → Show graph → Show Neo4j

3. GENERATION (45s)
   Chat → "Generate monthly revenue model" → Show SQL → Show trace

4. WRAP UP (30s)
   "Full observability, multi-agent, knowledge graph-powered"
```

**Total: 2.5 minutes + 30s buffer = 3 minutes**

---

**Remember:** Keep it simple. Show, don't tell. Let the technology speak for itself.

**You've got this! 🚀**