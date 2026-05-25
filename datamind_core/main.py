from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from langfuse import observe
import uuid, os, asyncio, traceback

load_dotenv("../.env")

from graph.workflow import datamind_graph
from graph.state import DataMindState

app = FastAPI(title="DataMind Core", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class ChatRequest(BaseModel):
    message:    str
    session_id: str = ""


class ChatResponse(BaseModel):
    answer:   str
    intent:   str
    trace_id: str
    details:  dict


@app.post("/chat", response_model=ChatResponse)
@observe(name="datamind_chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    trace_id   = str(uuid.uuid4())

    initial_state: DataMindState = {
        "user_query":        req.message,
        "session_id":        session_id,
        "intent":            None,
        "entities":          [],
        "discovery_result":  None,
        "lineage_result":    None,
        "generation_result": None,
        "cost_result":       None,
        "graph_context":     None,
        "answer":            None,
        "error":             None,
        "trace_id":          trace_id,
    }

    try:
        # Run sync LangGraph in thread pool so it doesn't block FastAPI
        result = await asyncio.to_thread(datamind_graph.invoke, initial_state)

        details = {}
        for k in ["discovery_result","lineage_result","generation_result","cost_result"]:
            if result.get(k):
                details = result[k]
                break

        return ChatResponse(
            answer   = result.get("answer") or "No answer returned.",
            intent   = str(result.get("intent", "unknown")),
            trace_id = trace_id,
            details  = details,
        )
    except Exception as e:
        print("CHAT ERROR:\n", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace_id": trace_id}
        )


# ── Cost summary for dashboard ───────────────────────────────
@app.get("/cost/summary")
async def cost_summary():
    try:
        from tools.snowflake_tool import get_query_costs
        from tools.snowflake_tool import _run as sf_run
        rows = await asyncio.to_thread(
            sf_run,
            "SELECT QUERY_ID, LEFT(QUERY_TEXT,200) AS query_text, USER_NAME,"
            " ROUND(EXECUTION_TIME/1000,2) AS exec_sec,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES,6) AS credits,"
            " ROUND(CREDITS_USED_CLOUD_SERVICES*2.0,4) AS est_usd"
            " FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY"
            " WHERE START_TIME>=DATEADD('day',-7,CURRENT_TIMESTAMP())"
            " AND EXECUTION_STATUS='SUCCESS'"
            " ORDER BY CREDITS_USED_CLOUD_SERVICES DESC LIMIT 20"
        )
        from collections import defaultdict
        daily = defaultdict(lambda: {"query_count":0,"total_credits":0.0,"total_usd":0.0})
        for r in rows:
            day = str(r.get("start_time",""))[:10] or "unknown"
            daily[day]["query_count"]   += 1
            daily[day]["total_credits"] += float(r.get("credits", 0))
            daily[day]["total_usd"]     += float(r.get("est_usd", 0))
        return {"daily": [{"day":k,**v} for k,v in sorted(daily.items())]}
    except Exception as e:
        return {"daily": [], "error": str(e)}


# ── MCP tools list ───────────────────────────────────────────
@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": [{
        "name":        "ask_datamind",
        "description": "Ask any question about your Snowflake data platform. Handles discovery, lineage tracing, dbt model generation, and query cost analysis.",
        "params":      ["message", "session_id"],
    }]}


# ── MCP streamable-http handler for Bob ─────────────────────
@app.post("/mcp")
async def mcp_handler(request: Request):
    body     = await request.json()
    method   = body.get("method", "")
    req_id   = body.get("id", 1)

    if method == "initialize":
        return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{
            "protocolVersion":"2024-11-05",
            "capabilities":{"tools":{}},
            "serverInfo":{"name":"datamind","version":"1.0.0"}
        }})

    elif method == "tools/list":
        return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{
            "tools":[{
                "name":"ask_datamind",
                "description":"Ask any question about your Snowflake data platform.",
                "inputSchema":{
                    "type":"object",
                    "properties":{
                        "message":    {"type":"string"},
                        "session_id": {"type":"string"}
                    },
                    "required":["message"]
                }
            }]
        }})

    elif method == "tools/call":
        params    = body.get("params", {})
        tool_name = params.get("name", "")
        args      = params.get("arguments", {})
        if tool_name == "ask_datamind":
            req    = ChatRequest(message=args.get("message",""),
                                 session_id=args.get("session_id",""))
            result = await chat(req)
            answer = result.answer if hasattr(result,"answer") else str(result)
            return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{
                "content":[{"type":"text","text":answer}],
                "isError":False
            }})

    elif method.startswith("notifications/"):
        return JSONResponse({"jsonrpc":"2.0","id":req_id,"result":{}})

    return JSONResponse({"jsonrpc":"2.0","id":req_id,
                         "error":{"code":-32601,"message":f"Unknown method: {method}"}})


# ── Health ───────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status":"ok","service":"datamind_core",
            "model": os.getenv("CORTEX_MODEL","not set")}