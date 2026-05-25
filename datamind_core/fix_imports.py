# Fix all relative imports to absolute imports
# Run from: datamind_core\

open('graph/workflow.py','w').write('''import httpx, os
from langgraph.graph import StateGraph, END
from graph.state import DataMindState, Intent
from graph.router import router_node, route_to_agent
from graph.agents.discovery  import discovery_agent_node
from graph.agents.lineage    import lineage_agent_node
from graph.agents.generation import generation_agent_node
from graph.agents.cost       import cost_agent_node

KNOWLEDGE_SVC = os.getenv("KNOWLEDGE_SVC_URL","http://localhost:8002")

def enrich_with_graph_context(state):
    entities = state.get("entities",[])
    if not entities:
        return state
    try:
        r = httpx.post(f"{KNOWLEDGE_SVC}/rag/context",
            json={"entities":entities,"query":state["user_query"]},timeout=10)
        ctx = r.json().get("context","") if r.status_code==200 else ""
    except Exception:
        ctx = ""
    return {**state,"graph_context":ctx}

def build_workflow():
    wf = StateGraph(DataMindState)
    wf.add_node("router",          router_node)
    wf.add_node("enrich",          enrich_with_graph_context)
    wf.add_node(Intent.DISCOVERY,  discovery_agent_node)
    wf.add_node(Intent.LINEAGE,    lineage_agent_node)
    wf.add_node(Intent.GENERATION, generation_agent_node)
    wf.add_node(Intent.COST,       cost_agent_node)
    wf.set_entry_point("router")
    wf.add_edge("router","enrich")
    wf.add_conditional_edges("enrich", route_to_agent, {
        Intent.DISCOVERY:  Intent.DISCOVERY,
        Intent.LINEAGE:    Intent.LINEAGE,
        Intent.GENERATION: Intent.GENERATION,
        Intent.COST:       Intent.COST,
    })
    for a in [Intent.DISCOVERY,Intent.LINEAGE,Intent.GENERATION,Intent.COST]:
        wf.add_edge(a, END)
    return wf.compile()

datamind_graph = build_workflow()
''')
print("Fixed: graph/workflow.py")

open('graph/router.py','w').write('''import re
from graph.state import DataMindState, Intent

LINEAGE_KW    = {"lineage","upstream","downstream","depends","where does","source of",
                 "what feeds","broken","trace","why did","root cause","impact"}
GENERATION_KW = {"generate","create model","write a dbt","build model","make a model",
                 "scaffold","new model","create a","write model"}
COST_KW       = {"cost","credits","expensive","optimize","slow query","performance",
                 "how much","billing","warehouse spend","query cost"}
DISCOVERY_KW  = {"find","search","list","what tables","show me","assets","which table",
                 "describe","metadata","columns","schema"}

def extract_entities(text):
    found = []
    for p in [r"\\b([a-z][a-z0-9_]{2,}(?:_[a-z0-9]+)+)\\b",
              r"\\b([A-Z_]{2,}\\.[A-Z_]{2,}\\.[A-Z_]{2,})\\b"]:
        found += re.findall(p, text)
    return list(set(found))

def router_node(state):
    q = state["user_query"].lower()
    if any(kw in q for kw in LINEAGE_KW):
        intent = Intent.LINEAGE
    elif any(kw in q for kw in GENERATION_KW):
        intent = Intent.GENERATION
    elif any(kw in q for kw in COST_KW):
        intent = Intent.COST
    else:
        intent = Intent.DISCOVERY
    return {**state, "intent": intent, "entities": extract_entities(state["user_query"])}

def route_to_agent(state):
    return state.get("intent", Intent.DISCOVERY).value
''')
print("Fixed: graph/router.py")

open('graph/agents/discovery.py','w').write('''import os
from graph.state import DataMindState
from tools.snowflake_tool import discover_assets, cortex_complete

def discovery_agent_node(state):
    query    = state["user_query"]
    entities = state.get("entities", [])
    ctx      = state.get("graph_context", "") or ""
    term     = entities[0] if entities else query.split()[-1].strip("?")
    assets   = discover_assets.run(term)
    asset_text = "\\n".join(
        f"- {a.get('table_name','')} ({a.get('table_type','')}, {a.get('row_count',0):,} rows)"
        for a in assets[:10]
    ) or "No matching assets found."
    answer = cortex_complete.run(
        f"User asked: {query}\\n\\n"
        f"Matching Snowflake assets:\\n{asset_text}\\n"
        f"Knowledge graph context:\\n{ctx}\\n\\n"
        f"Write a helpful 2-3 sentence answer. Use backticks for asset names."
    )
    return {**state,
            "discovery_result": {"assets": assets, "search_term": term},
            "answer": answer}
''')
print("Fixed: graph/agents/discovery.py")

open('graph/agents/lineage.py','w').write('''import httpx, os
from graph.state import DataMindState
from tools.snowflake_tool import cortex_complete

KNOWLEDGE_SVC = os.getenv("KNOWLEDGE_SVC_URL", "http://localhost:8002")

def lineage_agent_node(state):
    query    = state["user_query"]
    entities = state.get("entities", [])
    asset    = entities[0] if entities else ""
    if not asset:
        words = query.split()
        asset = next((w for w in words if "_" in w), words[-1])
    try:
        r = httpx.post(f"{KNOWLEDGE_SVC}/lineage/explain",
            json={"asset_name": asset, "direction": "both", "depth": 4},
            timeout=20)
        data = r.json() if r.status_code == 200 else {}
    except Exception as e:
        data = {"error": str(e), "paths": [], "count": 0}
    paths     = data.get("paths", [])
    path_text = "\\n".join(" -> ".join(p.get("chain",[])) for p in paths[:8]) or "No paths found."
    answer = cortex_complete.run(
        f"User asked: {query}\\n\\n"
        f"Lineage paths for {asset}:\\n{path_text}\\n\\n"
        f"Explain this lineage in plain English in 3-5 sentences. "
        f"Identify upstream sources and downstream dependents."
    )
    return {**state, "lineage_result": data, "answer": answer}
''')
print("Fixed: graph/agents/lineage.py")

open('graph/agents/generation.py','w').write('''import re
from graph.state import DataMindState
from tools.snowflake_tool import cortex_complete, run_sf_query

SYSTEM = """You are a senior dbt analytics engineer. Generate a production-ready dbt SQL model for Snowflake.
Use CTEs, ref() for model references, source() for raw tables. No SELECT *. Output ONLY valid SQL."""

def generation_agent_node(state):
    query = state["user_query"]
    ctx   = state.get("graph_context", "") or ""
    try:
        rows  = run_sf_query.run(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_SCHEMA NOT IN (\'INFORMATION_SCHEMA\') LIMIT 30")
        tlist = ", ".join(r.get("table_name","") for r in rows)
    except Exception:
        tlist = "ORDERS, CUSTOMERS, PRODUCTS"
    sql  = cortex_complete.run(
        f"{SYSTEM}\\n\\nAvailable tables: {tlist}\\nContext: {ctx}\\nRequest: {query}")
    name = "gen_" + re.sub(r"[^a-z0-9_]","_", query[:25].lower()).strip("_")
    name = re.sub(r"_+", "_", name)
    answer = (f"Generated dbt model: `{name}`\\n\\n"
              f"Save to: `models/marts/{name}.sql`\\n\\n"
              f"```sql\\n{sql}\\n```")
    return {**state,
            "generation_result": {"model_name": name, "sql": sql},
            "answer": answer}
''')
print("Fixed: graph/agents/generation.py")

open('graph/agents/cost.py','w').write('''from graph.state import DataMindState
from tools.snowflake_tool import get_query_costs, cortex_complete

def cost_agent_node(state):
    query = state["user_query"]
    costs = get_query_costs.run(7)
    summary = "\\n".join(
        f"{i+1}. [{r.get('exec_sec',0)}s | ${r.get('est_usd',0)}] {r.get('query_text','')[:80]}..."
        for i, r in enumerate(costs[:5])
    ) or "No cost data found for the last 7 days."
    tips = cortex_complete.run(
        f"Top expensive Snowflake queries:\\n{summary}\\n\\n"
        f"Question: {query}\\n\\n"
        f"For each query: root cause and one specific optimization. Be concise."
    )
    answer = f"**Top costly queries:**\\n\\n{summary}\\n\\n**Optimization tips:**\\n\\n{tips}"
    return {**state,
            "cost_result": {"queries": costs, "tips": tips},
            "answer": answer}
''')
print("Fixed: graph/agents/cost.py")

open('tools/snowflake_tool.py','w').write('''import snowflake.connector
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv("../.env")

def _conn():
    return snowflake.connector.connect(
        account  = os.getenv("SF_ACCOUNT"),
        user     = os.getenv("SF_USER"),
        password = os.getenv("SF_PASSWORD"),
        warehouse= os.getenv("SF_WAREHOUSE", "COMPUTE_WH"),
        database = os.getenv("SF_DATABASE",  "DATAMIND_DB"),
        schema   = os.getenv("SF_SCHEMA",    "PUBLIC"),
        role     = os.getenv("SF_ROLE",      "DATAMIND_ROLE"),
    )

def _run(sql, params=()):
    c = _conn(); cur = c.cursor(); cur.execute(sql, params)
    cols = [d[0].lower() for d in cur.description] if cur.description else []
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    c.close(); return rows

def _scalar(sql, params=()):
    c = _conn(); cur = c.cursor(); cur.execute(sql, params)
    row = cur.fetchone(); c.close()
    return row[0] if row else None

@tool
def discover_assets(search_term: str) -> list:
    """Find Snowflake tables/views matching a keyword in name or comment."""
    like = f"%{search_term}%"
    return _run(
        "SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, "
        "COALESCE(ROW_COUNT,0) AS row_count, COALESCE(COMMENT,\'\') AS comment "
        "FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA NOT IN (\'INFORMATION_SCHEMA\') "
        "AND (LOWER(TABLE_NAME) LIKE LOWER(%s) OR LOWER(COMMENT) LIKE LOWER(%s)) "
        "ORDER BY TABLE_NAME LIMIT 20", (like, like))

@tool
def run_sf_query(sql: str) -> list:
    """Execute a read-only Snowflake SQL query. Returns rows as list of dicts."""
    return _run(sql)

@tool
def cortex_complete(prompt: str) -> str:
    """Ask Snowflake Cortex to answer a prompt using AI."""
    model = os.getenv("CORTEX_MODEL", "snowflake-arctic")
    return _scalar("SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)", (model, prompt)) or ""

@tool
def get_query_costs(days: int = 7) -> list:
    """Return top 20 most expensive Snowflake queries in the last N days."""
    return _run(
        f"SELECT QUERY_ID, LEFT(QUERY_TEXT,200) AS query_text, USER_NAME, "
        f"ROUND(EXECUTION_TIME/1000,2) AS exec_sec, "
        f"ROUND(CREDITS_USED_CLOUD_SERVICES,6) AS credits, "
        f"ROUND(CREDITS_USED_CLOUD_SERVICES*2.0,4) AS est_usd "
        f"FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY "
        f"WHERE START_TIME >= DATEADD(\'day\',{-days},CURRENT_TIMESTAMP()) "
        f"AND EXECUTION_STATUS = \'SUCCESS\' "
        f"ORDER BY CREDITS_USED_CLOUD_SERVICES DESC LIMIT 20")
''')
print("Fixed: tools/snowflake_tool.py")
print()
print("All fixed! Now run: uvicorn main:app --host 0.0.0.0 --port 8001 --reload")