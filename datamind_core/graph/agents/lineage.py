import httpx, os
from graph.state import DataMindState
from tools.snowflake_tool import cortex_complete
from langfuse import observe

KNOWLEDGE_SVC = os.getenv("KNOWLEDGE_SVC_URL", "http://localhost:8002")

@observe(name="lineage_agent")
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
    path_text = "\n".join(" -> ".join(p.get("chain",[])) for p in paths[:8]) or "No paths found."
    answer = cortex_complete.run(
        f"User asked: {query}\n\n"
        f"Lineage paths for {asset}:\n{path_text}\n\n"
        f"Explain this lineage in plain English in 3-5 sentences. "
        f"Identify upstream sources and downstream dependents."
    )
    return {**state, "lineage_result": data, "answer": answer}
