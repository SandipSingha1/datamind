import os
from graph.state import DataMindState
from tools.snowflake_tool import discover_assets, cortex_complete
from langfuse import observe

@observe(name="discovery_agent")
def discovery_agent_node(state):
    query    = state["user_query"]
    entities = state.get("entities", [])
    ctx      = state.get("graph_context", "") or ""
    term     = entities[0] if entities else query.split()[-1].strip("?")
    assets   = discover_assets.run(term)
    asset_text = "\n".join(
        f"- {a.get('table_name','')} ({a.get('table_type','')}, {a.get('row_count',0):,} rows)"
        for a in assets[:10]
    ) or "No matching assets found."
    answer = cortex_complete.run(
        f"User asked: {query}\n\n"
        f"Matching Snowflake assets:\n{asset_text}\n"
        f"Knowledge graph context:\n{ctx}\n\n"
        f"Write a helpful 2-3 sentence answer. Use backticks for asset names."
    )
    return {**state,
            "discovery_result": {"assets": assets, "search_term": term},
            "answer": answer}
