from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv("../.env")

from neo4j_client import create_constraints
from graph_rag import get_graph_context, explain_lineage


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        create_constraints()
    except Exception as e:
        print(f"Neo4j startup warning: {e}")
    yield
    # Shutdown (if needed)


app = FastAPI(
    title="DataMind Knowledge Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class ContextRequest(BaseModel):
    entities: List[str]
    query:    str = ""


class LineageRequest(BaseModel):
    asset_name: str
    direction:  str = "both"
    depth:      int = 4


@app.post("/rag/context")
def rag_context(req: ContextRequest):
    ctx = get_graph_context(req.entities, req.query)
    return {"context": ctx, "entities": req.entities}


@app.post("/lineage/explain")
def lineage_explain(req: LineageRequest):
    return explain_lineage(req.asset_name, req.direction, req.depth)


@app.get("/health")
def health():
    return {"status": "ok", "service": "datamind_knowledge_svc"}
