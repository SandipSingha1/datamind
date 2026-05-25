import re
from graph.state import DataMindState, Intent
from langfuse import observe

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
    for p in [r"\b([a-z][a-z0-9_]{2,}(?:_[a-z0-9]+)+)\b",
              r"\b([A-Z_]{2,}\.[A-Z_]{2,}\.[A-Z_]{2,})\b"]:
        found += re.findall(p, text)
    return list(set(found))

@observe(name="router_node")
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
