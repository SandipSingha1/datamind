import httpx, os
from langgraph.graph import StateGraph, END
from langfuse import observe
from graph.state import DataMindState, Intent
from graph.router import router_node, route_to_agent
from graph.agents.discovery  import discovery_agent_node
from graph.agents.lineage    import lineage_agent_node
from graph.agents.generation import generation_agent_node
from graph.agents.cost       import cost_agent_node

KNOWLEDGE_SVC = os.getenv("KNOWLEDGE_SVC_URL","http://localhost:8002")

@observe(name="enrich_graph_context")
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
