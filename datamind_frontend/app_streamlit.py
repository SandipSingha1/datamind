import streamlit as st
import httpx
import uuid
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from functools import lru_cache

load_dotenv("../.env")

# Configuration
CORE = os.getenv("CORE_URL", "http://localhost:8001")
KNOW = os.getenv("KNOWLEDGE_URL", "http://localhost:8002")

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="DataMind - AI Data Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Optimized CSS - Reduced and streamlined
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    
    * { font-family: 'IBM Plex Sans', sans-serif; }
    #MainMenu, footer {visibility: hidden;}
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .main-header {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
        text-align: center;
    }
    
    .sub-header {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .team-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        color: white;
    }
    
    .team-name { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
    .team-tagline { font-size: 12px; font-style: italic; opacity: 0.9; margin-bottom: 12px; }
    .team-info { font-size: 12px; margin: 3px 0; opacity: 0.95; }
    .team-members { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 10px; }
    .member { background: rgba(255,255,255,0.2); padding: 6px 10px; border-radius: 6px; font-size: 11px; }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 16px 16px 4px 16px;
        margin: 10px 0;
        max-width: 75%;
        float: right;
        clear: both;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: white;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        padding: 14px 18px;
        border-radius: 16px 16px 16px 4px;
        margin: 10px 0;
        max-width: 75%;
        float: left;
        clear: both;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }
    
    .intent-badge {
        font-size: 10px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 10px;
        margin-top: 6px;
        display: inline-block;
        text-transform: uppercase;
    }
    
    .intent-discovery { background: #3b82f6; color: white; }
    .intent-lineage { background: #10b981; color: white; }
    .intent-generation { background: #8b5cf6; color: white; }
    .intent-cost { background: #f59e0b; color: white; }
    .intent-error { background: #ef4444; color: white; }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 3px 16px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .metric-label {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 6px;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .service-status {
        display: flex;
        align-items: center;
        margin: 6px 0;
        font-size: 12px;
        padding: 6px 10px;
        background: rgba(255,255,255,0.1);
        border-radius: 6px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #22c55e; }
    .status-offline { background-color: #ef4444; }
    
    .feature-card {
        background: white;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin: 10px 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #dbeafe 100%);
        border-left: 3px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 6px;
        margin: 14px 0;
        font-size: 13px;
        color: #1e40af;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 3px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 6px;
        margin: 14px 0;
        font-size: 13px;
        color: #92400e;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "page" not in st.session_state:
    st.session_state.page = "home"

# Cached service health check
@st.cache_data(ttl=10)
def check_service_cached(url, label):
    try:
        response = httpx.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False

# Sidebar
with st.sidebar:
    st.markdown('<div class="main-header">🧠 DataMind</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI Data Intelligence</div>', unsafe_allow_html=True)
    
    # Team Information Card
    st.markdown("""
    <div class="team-card">
        <div class="team-name">Neural Cluster-X0</div>
        <div class="team-tagline">"Ten Lines. One Cluster. Infinite Intelligence."</div>
        <div class="team-info"><strong>Service:</strong> Hybrid Cloud & Data</div>
        <div class="team-info"><strong>Track:</strong> Data Transformation</div>
        <div class="team-members">
            <div class="member">Sandip Singha</div>
            <div class="member">Debabrata Ghosh</div>
            <div class="member">Samyuktha Kuna</div>
            <div class="member">Swareena Kumari</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation - Using radio for better performance
    page = st.radio(
        "Navigation",
        ["🏠 Home", "💬 Chat", "🔗 Lineage", "💰 Cost", "🏗️ Architecture", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    # Update page state
    page_map = {
        "🏠 Home": "home",
        "💬 Chat": "chat",
        "🔗 Lineage": "lineage",
        "💰 Cost": "cost",
        "🏗️ Architecture": "architecture",
        "ℹ️ About": "about"
    }
    st.session_state.page = page_map[page]
    
    st.markdown("---")
    
    # Service health check
    st.markdown("**🔌 Service Status**")
    
    core_online = check_service_cached(f"{CORE}/health", "Core")
    know_online = check_service_cached(f"{KNOW}/health", "Knowledge")
    
    st.markdown(f'<div class="service-status"><div class="status-dot {"status-online" if core_online else "status-offline"}"></div>Core: {"Online" if core_online else "Offline"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="service-status"><div class="status-dot {"status-online" if know_online else "status-offline"}"></div>Knowledge: {"Online" if know_online else "Offline"}</div>', unsafe_allow_html=True)

# Main content area
if st.session_state.page == "home":
    st.title("🏠 Welcome to DataMind")
    st.markdown("*Your AI-Powered Data Intelligence Platform*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #3b82f6;">🔍 Discover</h3>
            <p style="color: #64748b; font-size: 13px;">
                Find tables and views with natural language queries.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #10b981;">🔗 Trace</h3>
            <p style="color: #64748b; font-size: 13px;">
                Visualize data lineage with Neo4j graph engine.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #8b5cf6;">⚡ Generate</h3>
            <p style="color: #64748b; font-size: 13px;">
                Create dbt models with Snowflake Cortex AI.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Platform Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #3b82f6;">🤖 AI Agents (4)</h4>
            <ul style="color: #64748b; font-size: 13px; line-height: 1.8;">
                <li><strong>Discovery Agent:</strong> Find tables & views</li>
                <li><strong>Lineage Agent:</strong> Trace dependencies</li>
                <li><strong>Generation Agent:</strong> Create dbt models</li>
                <li><strong>Cost Agent:</strong> Analyze query costs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #10b981;">🔧 Services (3)</h4>
            <ul style="color: #64748b; font-size: 13px; line-height: 1.8;">
                <li><strong>Core Service (8001):</strong> FastAPI + LangGraph</li>
                <li><strong>Knowledge Service (8002):</strong> Neo4j + Graph-RAG</li>
                <li><strong>Frontend (8050):</strong> Streamlit UI</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #8b5cf6;">🔌 Integrations (5)</h4>
            <ul style="color: #64748b; font-size: 13px; line-height: 1.8;">
                <li><strong>Snowflake:</strong> Data warehouse & Cortex AI</li>
                <li><strong>Neo4j:</strong> Graph database for lineage</li>
                <li><strong>dbt:</strong> Data transformation framework</li>
                <li><strong>Langfuse:</strong> Observability & tracing</li>
                <li><strong>Bob MCP:</strong> IBM assistant integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #f59e0b;">🛠️ Tech Stack</h4>
            <ul style="color: #64748b; font-size: 13px; line-height: 1.8;">
                <li><strong>LangGraph:</strong> Agent orchestration</li>
                <li><strong>FastAPI:</strong> High-performance APIs</li>
                <li><strong>Streamlit:</strong> Interactive web UI</li>
                <li><strong>Plotly:</strong> Data visualizations</li>
                <li><strong>Pydantic:</strong> Data validation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>💡 Quick Start:</strong><br>
        1. Go to <strong>Chat</strong> to ask questions<br>
        2. Use <strong>Lineage</strong> to visualize dependencies<br>
        3. Check <strong>Cost</strong> for optimization insights
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "chat":
    st.title("💬 Chat with Bob")
    st.markdown("*Ask anything about your data platform*")
    
    # Suggestions
    st.markdown("**💡 Try these:**")
    suggestions = [
        "Find tables related to orders",
        "Show lineage for fct_orders",
        "Generate monthly revenue model",
        "Which queries cost most?",
    ]
    
    cols = st.columns(len(suggestions))
    for i, (col, suggestion) in enumerate(zip(cols, suggestions)):
        if col.button(suggestion, key=f"sug_{i}"):
            st.session_state.chat_history.append({"role": "user", "text": suggestion, "intent": ""})
            
            with st.spinner("🤔 Thinking..."):
                try:
                    response = httpx.post(
                        f"{CORE}/chat",
                        json={"message": suggestion, "session_id": st.session_state.session_id},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "No answer.")
                        intent = data.get("intent", "unknown")
                    else:
                        answer = f"Error {response.status_code}"
                        intent = "error"
                except Exception as e:
                    answer = f"Error: {str(e)}"
                    intent = "error"
            
            st.session_state.chat_history.append({"role": "assistant", "text": answer, "intent": intent})
            st.rerun()
    
    # Chat history
    if not st.session_state.chat_history:
        st.markdown('<div class="info-box">👋 <strong>Welcome!</strong> Ask me anything about your data platform.</div>', unsafe_allow_html=True)
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["text"]}</div>', unsafe_allow_html=True)
        else:
            intent_str = str(msg.get("intent", "")).split(".")[-1].lower()
            intent_class = f"intent-{intent_str}" if intent_str in ["discovery", "lineage", "generation", "cost", "error"] else "intent-discovery"
            answer_html = msg["text"].replace("\n", "<br>")
            st.markdown(f'<div class="assistant-message">{answer_html}<br><span class="intent-badge {intent_class}">{intent_str}</span></div>', unsafe_allow_html=True)
    
    st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    user_input = st.text_input("Your message:", placeholder="e.g. Find tables related to orders", label_visibility="collapsed")
    
    col1, col2 = st.columns([5, 1])
    with col2:
        send_button = st.button("Send 📤", type="primary", use_container_width=True)
    
    if send_button and user_input:
        st.session_state.chat_history.append({"role": "user", "text": user_input, "intent": ""})
        
        with st.spinner("🤔 Thinking..."):
            try:
                response = httpx.post(
                    f"{CORE}/chat",
                    json={"message": user_input, "session_id": st.session_state.session_id},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer.")
                    intent = data.get("intent", "unknown")
                else:
                    answer = f"Error {response.status_code}"
                    intent = "error"
            except Exception as e:
                answer = f"Error: {str(e)}"
                intent = "error"
        
        st.session_state.chat_history.append({"role": "assistant", "text": answer, "intent": intent})
        st.rerun()
    
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

elif st.session_state.page == "lineage":
    st.title("🔗 Lineage Explorer")
    st.markdown("*Visualize data lineage from Neo4j*")
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        asset_name = st.text_input("Asset Name:", placeholder="e.g. fct_orders")
    with col2:
        direction = st.selectbox("Direction:", ["both", "upstream", "downstream"])
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        explore_button = st.button("🔍 Explore", type="primary")
    
    if explore_button and asset_name:
        with st.spinner("🔄 Fetching lineage..."):
            try:
                response = httpx.post(
                    f"{KNOW}/lineage/explain",
                    json={"asset_name": asset_name, "direction": direction, "depth": 4},
                    timeout=20
                )
                
                # Check response status
                if response.status_code != 200:
                    st.error(f"❌ Error {response.status_code}: {response.text[:200]}")
                    st.info("💡 Make sure the Knowledge Service is running on port 8002")
                else:
                    try:
                        data = response.json()
                    except Exception as json_error:
                        st.error(f"❌ Invalid JSON response: {str(json_error)}")
                        st.info("💡 The Knowledge Service returned an invalid response. Check if Neo4j is running.")
                        data = {}
                    
                    paths = data.get("paths", [])
                    count = data.get("count", 0)
                    
                    if count == 0:
                        st.warning(f"⚠️ No paths found for {asset_name}")
                    else:
                        st.success(f"✅ Found {count} paths for **{asset_name}**")
                    
                    st.markdown("### 🛤️ Lineage Paths")
                    for i, path in enumerate(paths[:10], 1):
                        chain = path.get("chain", [])
                        path_str = " → ".join([f"`{node}`" for node in chain])
                        st.markdown(f"{i}. {path_str}")
                    
                    if count > 10:
                        st.info(f"ℹ️ Showing first 10 of {count} paths")
                    
                    # Network data
                    nodes = []
                    edges = []
                    seen_nodes = set()
                    seen_edges = set()
                    
                    for path in paths:
                        chain = path.get("chain", [])
                        rels = path.get("rels", [])
                        
                        for name in chain:
                            if name not in seen_nodes:
                                seen_nodes.add(name)
                                node_type = "dbt model" if any(x in name for x in ["fct_", "dim_", "stg_", "mart_"]) else "Snowflake table"
                                nodes.append({"Asset": name, "Type": node_type})
                        
                        for i in range(len(chain) - 1):
                            edge_key = (chain[i], chain[i+1])
                            if edge_key not in seen_edges:
                                seen_edges.add(edge_key)
                                rel = rels[i] if i < len(rels) else "DEPENDS_ON"
                                edges.append({"Source": chain[i], "Target": chain[i+1], "Relationship": rel})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if nodes:
                            st.markdown(f"**📦 Nodes ({len(nodes)})**")
                            st.dataframe(pd.DataFrame(nodes), use_container_width=True, height=300)
                    with col2:
                        if edges:
                            st.markdown(f"**🔗 Edges ({len(edges)})**")
                            st.dataframe(pd.DataFrame(edges), use_container_width=True, height=300)
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

elif st.session_state.page == "cost":
    st.title("💰 Cost Dashboard")
    st.markdown("*Snowflake query cost — last 7 days*")
    
    @st.cache_data(ttl=60)
    def get_cost_data():
        try:
            response = httpx.get(f"{CORE}/cost/summary", timeout=20)
            if response.status_code == 200:
                return response.json().get("daily", [])
        except:
            pass
        return []
    
    daily = get_cost_data()
    
    if daily:
        df = pd.DataFrame(daily)
        
        for col in ["query_count", "total_credits", "total_usd"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        
        total_queries = int(df["query_count"].sum()) if "query_count" in df.columns else 0
        total_credits = round(float(df["total_credits"].sum()), 4) if "total_credits" in df.columns else 0
        total_usd = round(float(df["total_usd"].sum()), 2) if "total_usd" in df.columns else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">📊 Queries</div><div class="metric-value">{total_queries:,}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">⚡ Credits</div><div class="metric-value">{total_credits}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">💵 Cost</div><div class="metric-value" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${total_usd}</div></div>', unsafe_allow_html=True)
        
        if "day" in df.columns and "total_usd" in df.columns:
            st.markdown("### 📈 Daily Cost")
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["day"],
                y=df["total_usd"],
                marker_color='#3b82f6',
                text=df["total_usd"].apply(lambda x: f"${x:.2f}"),
                textposition='outside'
            ))
            
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(l=40, r=40, t=20, b=40),
                xaxis_title="Date",
                yaxis_title="Cost (USD)",
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Details")
        st.dataframe(df, use_container_width=True, height=250)
    else:
        st.info("ℹ️ No cost data yet. Run some Snowflake queries first.")

elif st.session_state.page == "architecture":
    st.title("🏗️ System Architecture")
    st.markdown("*How DataMind Works Under the Hood*")
    
    # Architecture Overview
    st.markdown("### 📐 High-Level Architecture")
    st.markdown("""
    <div class="feature-card">
        <p style="font-size: 14px; line-height: 1.8; color: #475569;">
            DataMind follows a <strong>microservices architecture</strong> with three main services orchestrated through
            <strong>LangGraph agents</strong>. The system integrates <strong>Snowflake</strong> for data warehousing,
            <strong>Neo4j</strong> for graph-based lineage, and <strong>Snowflake Cortex AI</strong> for intelligent responses.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mermaid Architecture Diagram
    st.markdown("### 🎨 Visual Architecture Diagram")
    
    mermaid_code = """
    ```mermaid
    graph TB
        subgraph "USER INTERFACE LAYER"
            A[Streamlit Frontend<br/>Port 8050<br/>Chat, Lineage, Cost Dashboard]
        end
        
        subgraph "CORE ORCHESTRATION LAYER - Port 8001"
            B[FastAPI Application<br/>Endpoints: /chat, /mcp, /cost]
            
            subgraph "LangGraph Workflow"
                C[Router Node<br/>Intent Classification]
                D[Enrich Node<br/>Graph Context]
                E1[Discovery Agent<br/>Find Tables]
                E2[Lineage Agent<br/>Trace Dependencies]
                E3[Generation Agent<br/>Create dbt Models]
                E4[Cost Agent<br/>Query Analysis]
            end
        end
        
        subgraph "KNOWLEDGE GRAPH LAYER - Port 8002"
            F[Knowledge Service<br/>FastAPI + Graph-RAG]
            G[(Neo4j Database<br/>Port 7474, 7687<br/>Data Lineage Graph)]
        end
        
        subgraph "EXTERNAL DATA LAYER"
            H[(Snowflake<br/>Data Warehouse<br/>Tables, Query History, Cortex AI)]
        end
        
        subgraph "DATA TRANSFORMATION"
            I[dbt Project<br/>manifest.json<br/>SQL Models]
        end
        
        subgraph "OBSERVABILITY"
            J[Langfuse<br/>Tracing]
            K[Bob MCP<br/>JSON-RPC 2.0]
        end
        
        A -->|HTTP REST| B
        B --> C
        C --> D
        D --> E1
        D --> E2
        D --> E3
        D --> E4
        
        D -.->|Graph Context| F
        E2 -.->|Lineage Query| F
        F --> G
        
        E1 -->|SQL Queries| H
        E3 -->|SQL Queries| H
        E4 -->|SQL Queries| H
        
        I -.->|Metadata Ingestion| G
        
        J -.->|Traces| B
        K -.->|MCP Protocol| B
        
        style A fill:#dae8fc,stroke:#6c8ebf
        style B fill:#fff2cc,stroke:#d6b656
        style C fill:#ffe6cc,stroke:#d79b00
        style D fill:#ffe6cc,stroke:#d79b00
        style E1 fill:#b1ddf0,stroke:#10739e
        style E2 fill:#b1ddf0,stroke:#10739e
        style E3 fill:#b1ddf0,stroke:#10739e
        style E4 fill:#b1ddf0,stroke:#10739e
        style F fill:#fff2cc,stroke:#d6b656
        style G fill:#d5e8d4,stroke:#82b366
        style H fill:#fff2cc,stroke:#d6b656
        style I fill:#ffe6cc,stroke:#d79b00
        style J fill:#d5e8d4,stroke:#82b366
        style K fill:#d5e8d4,stroke:#82b366
    ```
    """
    
    st.code(mermaid_code, language="mermaid")
    
    st.markdown("""
    <div class="info-box">
        💡 <strong>How to view this diagram:</strong><br>
        1. Copy the Mermaid code above<br>
        2. Go to <a href="https://mermaid.live/" target="_blank" style="color: #3b82f6;">mermaid.live</a><br>
        3. Paste and view the interactive diagram<br>
        4. Or use a Mermaid viewer extension in your browser
    </div>
    """, unsafe_allow_html=True)
    
    # System Layers
    st.markdown("### 🎯 System Layers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #3b82f6;">1️⃣ Frontend Layer</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.7;">
                <strong>Technology:</strong> Streamlit + Plotly<br>
                <strong>Port:</strong> 8050<br>
                <strong>Purpose:</strong> User interface for chat, lineage visualization, and cost analytics<br>
                <strong>Communication:</strong> HTTP REST API calls to Core Service
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #10b981;">3️⃣ Knowledge Graph Layer</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.7;">
                <strong>Technology:</strong> FastAPI + Neo4j + Graph-RAG<br>
                <strong>Port:</strong> 8002<br>
                <strong>Purpose:</strong> Store and query data lineage graph<br>
                <strong>Database:</strong> Neo4j (Ports 7474, 7687)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #8b5cf6;">2️⃣ Core Orchestration Layer</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.7;">
                <strong>Technology:</strong> FastAPI + LangGraph + LangChain<br>
                <strong>Port:</strong> 8001<br>
                <strong>Purpose:</strong> Agent orchestration and workflow management<br>
                <strong>Agents:</strong> Discovery, Lineage, Generation, Cost
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #f59e0b;">4️⃣ External Data Layer</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.7;">
                <strong>Technology:</strong> Snowflake Data Warehouse<br>
                <strong>Purpose:</strong> Data storage, query execution, AI (Cortex)<br>
                <strong>Features:</strong> INFORMATION_SCHEMA, ACCOUNT_USAGE, Cortex AI
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Request Flow
    st.markdown("### 🔄 Request Flow Diagram")
    
    st.markdown("""
    <div class="feature-card">
        <h4 style="color: #1e293b;">User Query → Response Journey</h4>
        <div style="font-family: monospace; font-size: 12px; line-height: 2; color: #475569; padding: 10px; background: #f8fafc; border-radius: 8px; margin-top: 12px;">
            <strong style="color: #3b82f6;">1. User Input</strong><br>
            &nbsp;&nbsp;↓ User asks: "Find tables related to orders"<br>
            &nbsp;&nbsp;↓ Frontend (Streamlit) → POST /chat<br>
            <br>
            <strong style="color: #8b5cf6;">2. Core Service (Port 8001)</strong><br>
            &nbsp;&nbsp;↓ Receives request<br>
            &nbsp;&nbsp;↓ Starts Langfuse trace<br>
            &nbsp;&nbsp;↓ Invokes LangGraph workflow<br>
            <br>
            <strong style="color: #10b981;">3. Router Node</strong><br>
            &nbsp;&nbsp;↓ Analyzes query keywords<br>
            &nbsp;&nbsp;↓ Classifies intent: DISCOVERY<br>
            &nbsp;&nbsp;↓ Extracts entities: ["orders"]<br>
            <br>
            <strong style="color: #10b981;">4. Enrich Node</strong><br>
            &nbsp;&nbsp;↓ Calls Knowledge Service (Port 8002)<br>
            &nbsp;&nbsp;↓ POST /rag/context with entities<br>
            &nbsp;&nbsp;↓ Neo4j queries graph for context<br>
            &nbsp;&nbsp;↓ Returns: relationships, metadata<br>
            <br>
            <strong style="color: #3b82f6;">5. Discovery Agent</strong><br>
            &nbsp;&nbsp;↓ Queries Snowflake INFORMATION_SCHEMA<br>
            &nbsp;&nbsp;↓ Finds matching tables: orders, order_items, order_status<br>
            &nbsp;&nbsp;↓ Calls Snowflake Cortex AI<br>
            &nbsp;&nbsp;↓ Generates natural language response<br>
            <br>
            <strong style="color: #f59e0b;">6. Response</strong><br>
            &nbsp;&nbsp;↓ Langfuse logs trace<br>
            &nbsp;&nbsp;↓ Returns JSON to Frontend<br>
            &nbsp;&nbsp;↓ User sees: "Found 3 tables: orders, order_items, order_status..."<br>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent Workflows
    st.markdown("### 🤖 Agent Workflows")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Discovery", "🔗 Lineage", "⚡ Generation", "💰 Cost"])
    
    with tab1:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #3b82f6;">Discovery Agent Workflow</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.8;">
                <strong>Trigger:</strong> Keywords like "find", "search", "list", "what tables"<br><br>
                <strong>Steps:</strong><br>
                1. Extract search term from query<br>
                2. Query Snowflake INFORMATION_SCHEMA.TABLES<br>
                3. Filter by table name or comment (LIKE search)<br>
                4. Get table metadata (type, row count, comment)<br>
                5. Use Cortex AI to generate natural language response<br>
                6. Return formatted list of matching assets<br><br>
                <strong>Output:</strong> List of tables/views with descriptions
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #10b981;">Lineage Agent Workflow</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.8;">
                <strong>Trigger:</strong> Keywords like "lineage", "upstream", "downstream", "depends"<br><br>
                <strong>Steps:</strong><br>
                1. Extract asset name from query<br>
                2. Call Knowledge Service /lineage/explain<br>
                3. Neo4j traverses graph (DEPENDS_ON, READS_FROM, WRITES_TO)<br>
                4. Returns paths up to depth 4<br>
                5. Use Cortex AI to explain lineage in plain English<br>
                6. Return paths and explanation<br><br>
                <strong>Output:</strong> Lineage paths with upstream/downstream dependencies
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #8b5cf6;">Generation Agent Workflow</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.8;">
                <strong>Trigger:</strong> Keywords like "generate", "create model", "write dbt"<br><br>
                <strong>Steps:</strong><br>
                1. Query Snowflake for available tables<br>
                2. Get graph context from Knowledge Service<br>
                3. Build prompt with table list and requirements<br>
                4. Use Cortex AI to generate dbt SQL model<br>
                5. Format with CTEs, ref(), source() functions<br>
                6. Generate model name from query<br><br>
                <strong>Output:</strong> Production-ready dbt SQL model code
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #f59e0b;">Cost Agent Workflow</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.8;">
                <strong>Trigger:</strong> Keywords like "cost", "expensive", "optimize", "slow query"<br><br>
                <strong>Steps:</strong><br>
                1. Query SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY<br>
                2. Get top 20 expensive queries (last 7 days)<br>
                3. Calculate credits used and estimated USD cost<br>
                4. Use Cortex AI to analyze and suggest optimizations<br>
                5. Return cost data with optimization tips<br><br>
                <strong>Output:</strong> Query cost analysis with optimization recommendations
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Data Flow
    st.markdown("### 📊 Data Flow Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #3b82f6;">Synchronous Flow</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.7;">
                <strong>User → Frontend → Core → Agent → External Service → Response</strong><br><br>
                • User sends query<br>
                • Frontend makes HTTP POST<br>
                • Core orchestrates workflow<br>
                • Agent executes logic<br>
                • External service provides data<br>
                • Response flows back to user
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4 style="color: #10b981;">Asynchronous Tracing</h4>
            <p style="font-size: 13px; color: #64748b; line-height: 1.7;">
                <strong>Langfuse Observability (Parallel)</strong><br><br>
                • Every agent execution traced<br>
                • LLM calls logged with tokens<br>
                • Execution time measured<br>
                • Errors captured<br>
                • Traces sent to Langfuse<br>
                • Available for debugging
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown("### 🛠️ Technology Stack Details")
    
    tech_details = {
        "LangGraph": "Workflow orchestration framework for building stateful, multi-agent applications",
        "FastAPI": "Modern, fast web framework for building APIs with Python 3.7+",
        "Streamlit": "Open-source app framework for Machine Learning and Data Science",
        "Neo4j": "Graph database for storing and querying complex relationships",
        "Snowflake": "Cloud data warehouse with built-in AI capabilities (Cortex)",
        "Langfuse": "Open-source LLM engineering platform for tracing and monitoring",
        "Pydantic": "Data validation using Python type annotations",
        "Plotly": "Interactive graphing library for Python",
        "dbt": "Data transformation tool that enables analytics engineers to transform data",
        "HTTPX": "Fully featured HTTP client for Python 3"
    }
    
    for tech, desc in tech_details.items():
        st.markdown(f"""
        <div class="feature-card">
            <h4 style="color: #1e293b; font-size: 15px;">{tech}</h4>
            <p style="font-size: 12px; color: #64748b;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Integration Points
    st.markdown("### 🔌 Integration Points")
    
    st.markdown("""
    <div class="feature-card">
        <h4 style="color: #1e293b;">Bob MCP Integration</h4>
        <p style="font-size: 13px; color: #64748b; line-height: 1.7;">
            <strong>Protocol:</strong> Model Context Protocol (MCP) via JSON-RPC 2.0<br>
            <strong>Endpoint:</strong> POST /mcp<br>
            <strong>Tool Exposed:</strong> ask_datamind<br>
            <strong>Methods Supported:</strong><br>
            • initialize - Setup connection<br>
            • tools/list - List available tools<br>
            • tools/call - Execute tool with parameters<br>
            • notifications/* - Handle notifications<br><br>
            <strong>Usage:</strong> Bob can call DataMind as a tool to answer data-related questions
        </p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "about":
    st.title("ℹ️ About DataMind")
    st.markdown("*AI-Powered Data Intelligence Platform*")
    
    st.markdown("### 🎯 Project Overview")
    st.markdown("""
    <div class="feature-card">
        <p style="font-size: 14px; line-height: 1.7; color: #475569;">
            DataMind is an AI-powered platform built for <strong>IBM Bob-a-thon 2026</strong>. 
            It combines LangGraph, Neo4j, and Snowflake Cortex for intelligent data discovery, 
            lineage tracking, and AI-driven insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👥 Team Neural Cluster-X0")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>Team Details</h4>
            <p style="font-size: 13px; line-height: 1.7; color: #64748b;">
                <strong>Name:</strong> Neural Cluster-X0<br>
                <strong>Service:</strong> Hybrid Cloud & Data<br>
                <strong>Track:</strong> Data Transformation<br>
                <strong>Tagline:</strong> <em>"Ten Lines. One Cluster. Infinite Intelligence."</em>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>Team Members</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 12px;">
                <div style="background: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #475569;">Sandip Singha</div>
                <div style="background: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #475569;">Debabrata Ghosh</div>
                <div style="background: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #475569;">Samyuktha Kuna</div>
                <div style="background: #f1f5f9; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #475569;">Swareena Kumari</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### ✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔍 Discovery Agent</h4>
            <p style="font-size: 13px; color: #64748b;">Find tables using natural language</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>⚡ Generation Agent</h4>
            <p style="font-size: 13px; color: #64748b;">Auto-generate dbt models</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🔗 Lineage Agent</h4>
            <p style="font-size: 13px; color: #64748b;">Trace data dependencies</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h4>💰 Cost Agent</h4>
            <p style="font-size: 13px; color: #64748b;">Analyze query costs</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px; padding: 16px;">
    <strong style="color: #667eea;">DataMind</strong> by <strong style="color: #667eea;">Neural Cluster-X0</strong> | IBM Bob-a-thon 2026<br>
    <em>"Ten Lines. One Cluster. Infinite Intelligence."</em>
</div>
""", unsafe_allow_html=True)

# Made with Bob
