import re
from graph.state import DataMindState
from tools.snowflake_tool import cortex_complete, run_sf_query
from langfuse import observe

SYSTEM = """You are a senior dbt analytics engineer. Generate a production-ready dbt SQL model for Snowflake.
Use CTEs, ref() for model references, source() for raw tables. No SELECT *. Output ONLY valid SQL."""

@observe(name="generation_agent")
def generation_agent_node(state):
    query = state["user_query"]
    ctx   = state.get("graph_context", "") or ""
    try:
        rows  = run_sf_query.run(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA') LIMIT 30")
        tlist = ", ".join(r.get("table_name","") for r in rows)
    except Exception:
        tlist = "ORDERS, CUSTOMERS, PRODUCTS"
    sql  = cortex_complete.run(
        f"{SYSTEM}\n\nAvailable tables: {tlist}\nContext: {ctx}\nRequest: {query}")
    name = "gen_" + re.sub(r"[^a-z0-9_]","_", query[:25].lower()).strip("_")
    name = re.sub(r"_+", "_", name)
    answer = (f"Generated dbt model: `{name}`\n\n"
              f"Save to: `models/marts/{name}.sql`\n\n"
              f"```sql\n{sql}\n```")
    return {**state,
            "generation_result": {"model_name": name, "sql": sql},
            "answer": answer}
