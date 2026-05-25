from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum


class Intent(str, Enum):
    DISCOVERY  = "discovery"
    LINEAGE    = "lineage"
    GENERATION = "generation"
    COST       = "cost"
    UNKNOWN    = "unknown"


class DataMindState(TypedDict):
    # Input
    user_query:  str
    session_id:  str

    # Routing
    intent:    Optional[Intent]
    entities:  List[str]          # table/model names extracted from query

    # Agent results
    discovery_result:  Optional[Dict[str, Any]]
    lineage_result:    Optional[Dict[str, Any]]
    generation_result: Optional[Dict[str, Any]]
    cost_result:       Optional[Dict[str, Any]]

    # Context from Neo4j (injected before agents run)
    graph_context: Optional[str]

    # Final output
    answer:   Optional[str]
    error:    Optional[str]
    trace_id: Optional[str]
