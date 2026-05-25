# DataMind_Full_Implementation.docx - Required Updates

## Summary of Changes
**Dash has been removed** from the DataMind project. The frontend now uses **Streamlit** exclusively. This document lists all required updates to the Word document.

---

## 1. Title Page (Line 15)
**CHANGE:**
```
Snowflake + dbt + LangChain + LangFuse + LangSmith + Dash
```
**TO:**
```
Snowflake + dbt + LangChain + LangFuse + LangSmith + Streamlit
```

---

## 2. Architecture Overview (Line 23)
**CHANGE:**
```
datamind_frontend (Dash) is the user-facing UI.
```
**TO:**
```
datamind_frontend (Streamlit) is the user-facing UI.
```

---

## 3. Service Map Table (Lines 61-69)
**CHANGE:**
```
datamind_frontend | Frontend | 8050 | Dash + Plotly + Cytoscape | Chat UI, lineage visualizer, cost dashboard
```
**TO:**
```
datamind_frontend | Frontend | 8050 | Streamlit + Plotly | Chat UI, lineage visualizer, cost dashboard
```

---

## 4. User Query Flow Table (Lines 87-89)
**CHANGE:**
```
1 | User types a question into the Dash chat UI or asks Bob directly | datamind_frontend
```
**TO:**
```
1 | User types a question into the Streamlit chat UI or asks Bob directly | datamind_frontend
```

**CHANGE:**
```
8 | Answer streams back to Bob / Dash frontend | datamind_frontend
```
**TO:**
```
8 | Answer streams back to Bob / Streamlit frontend | datamind_frontend
```

---

## 5. Folder Structure (Lines 189-204)
**CHANGE:**
```
├── datamind_frontend/          ← Service 3
│   ├── app.py                 ← Dash entry point
│   ├── pages/
│   │   ├── chat.py
│   │   ├── lineage.py
│   │   └── cost.py
│   └── components/
│       └── sidebar.py
```
**TO:**
```
├── datamind_frontend/          ← Service 3
│   └── app_streamlit.py       ← Streamlit entry point
```

---

## 6. Install Dependencies (Lines 243-246)
**CHANGE:**
```
# Service 3 — Frontend
dash dash-cytoscape plotly pandas \
```
**TO:**
```
# Service 3 — Frontend
streamlit plotly pandas \
```

---

## 7. Section 5 Title (Line 1859)
**CHANGE:**
```
5.  Service 3 — datamind_frontend (Dash)
```
**TO:**
```
5.  Service 3 — datamind_frontend (Streamlit)
```

**CHANGE:**
```
Dash is a Python framework for building web applications — no JavaScript needed. The frontend has three pages: Chat (talks to datamind_core), Lineage Explorer (visualizes Neo4j paths with Cytoscape), and Cost Dashboard (Plotly charts from Snowflake).
```
**TO:**
```
Streamlit is a Python framework for building data applications with minimal code. The frontend has three pages: Chat (talks to datamind_core), Lineage Explorer (visualizes Neo4j paths), and Cost Dashboard (Plotly charts from Snowflake).
```

---

## 8. Section 5.1 - COMPLETELY REPLACE (Lines 1865-1982)
**DELETE:** Entire section "5.1 app.py — Dash entry point with sidebar"

**REPLACE WITH:**
```
5.1  app_streamlit.py — Streamlit entry point

PYTHON — DATAMIND_FRONTEND/APP_STREAMLIT.PY

import streamlit as st
import httpx
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv("../.env")

CORE_URL = "http://localhost:8001"
KNOWLEDGE_URL = "http://localhost:8002"

st.set_page_config(page_title="DataMind", page_icon="🧠", layout="wide")

# Sidebar navigation
with st.sidebar:
    st.title("🧠 DataMind")
    st.caption("AI Data Intelligence")
    
    page = st.radio(
        "Navigation",
        ["💬 Chat with Bob", "🔗 Lineage Explorer", "💰 Cost Dashboard"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.caption("**Services**")
    st.caption("Core: localhost:8001")
    st.caption("Knowledge: localhost:8002")

# Page routing
if "💬 Chat" in page:
    # Chat page implementation
    st.header("Chat with Bob")
    st.caption("Ask anything about your data platform")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Call DataMind Core
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    r = httpx.post(
                        f"{CORE_URL}/chat",
                        json={"message": prompt, "session_id": st.session_state.session_id},
                        timeout=60
                    )
                    data = r.json()
                    answer = data.get("answer", "No answer returned.")
                    st.write(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")

elif "🔗 Lineage" in page:
    # Lineage Explorer page
    st.header("Lineage Explorer")
    st.caption("Visualize data lineage from Neo4j")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        asset_name = st.text_input("Asset name", placeholder="e.g., fct_orders")
    with col2:
        direction = st.selectbox("Direction", ["both", "upstream", "downstream"])
    with col3:
        depth = st.slider("Depth", 1, 6, 3)
    
    if st.button("Explore", type="primary"):
        if asset_name:
            try:
                r = httpx.post(
                    f"{KNOWLEDGE_URL}/lineage/explain",
                    json={"asset_name": asset_name, "direction": direction, "depth": depth},
                    timeout=20
                )
                data = r.json()
                paths = data.get("paths", [])
                
                st.success(f"Found {len(paths)} lineage paths")
                
                for i, path in enumerate(paths[:10]):
                    chain = path.get("chain", [])
                    st.text(f"{i+1}. {' → '.join(chain)}")
            except Exception as e:
                st.error(f"Error: {e}")

elif "💰 Cost" in page:
    # Cost Dashboard page
    st.header("Cost Dashboard")
    st.caption("Snowflake query cost — last 7 days")
    
    try:
        r = httpx.get(f"{CORE_URL}/cost/summary", timeout=30)
        daily = r.json().get("daily", [])
        df = pd.DataFrame(daily)
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Queries", int(df["query_count"].sum()))
            with col2:
                st.metric("Total Cost (USD)", f"${df['total_usd'].sum():.2f}")
            with col3:
                st.metric("Total Credits", f"{df['total_credits'].sum():.4f}")
            
            fig = px.bar(df, x="day", y="total_usd", 
                        labels={"total_usd": "USD", "day": "Date"},
                        color_discrete_sequence=["#0F62FE"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost data available")
    except Exception as e:
        st.error(f"Error loading cost data: {e}")

if __name__ == "__main__":
    pass  # Streamlit runs automatically
```

---

## 9. DELETE Sections 5.2, 5.3, 5.4 (Lines 1985-2524)
**DELETE:** All Dash page implementations:
- 5.2 pages/chat.py
- 5.3 pages/lineage.py  
- 5.4 pages/cost.py

**REPLACE WITH:**
```
5.2  Running the Streamlit App

BASH
cd datamind_frontend
streamlit run app_streamlit.py

The app will automatically open at http://localhost:8050 in your browser.

Key Features:
- **Chat with Bob**: Natural language interface to all DataMind agents
- **Lineage Explorer**: Visual graph of data dependencies from Neo4j
- **Cost Dashboard**: Real-time Snowflake query cost analytics

All three pages are in a single file (app_streamlit.py) using Streamlit's native page routing.
```

---

## 10. Running Everything - Step 6 (Line 2573)
**CHANGE:**
```
6. Start frontend | cd datamind_frontend && python app.py | Tab 4
```
**TO:**
```
6. Start frontend | cd datamind_frontend && streamlit run app_streamlit.py | Tab 4
```

---

## 11. run.sh Script (Line 2625)
**CHANGE:**
```
cd datamind_frontend && python app.py &
```
**TO:**
```
cd datamind_frontend && streamlit run app_streamlit.py &
```

**CHANGE:**
```
echo '  Dash UI:          http://localhost:8050'
```
**TO:**
```
echo '  Streamlit UI:     http://localhost:8050'
```

---

## 12. Demo Script Table (Lines 2776-2796)
**CHANGE:**
```
0:00-0:30 | Open Dash at localhost:8050. Say: 'DataMind gives IBM Bob...' | Judges see the Dash chat UI...
```
**TO:**
```
0:00-0:30 | Open Streamlit at localhost:8050. Say: 'DataMind gives IBM Bob...' | Judges see the Streamlit chat UI...
```

**CHANGE:**
```
2:30-3:00 | Back to chat. Type: 'Generate a dbt model...' | ...SQL displayed in chat...
```
**TO:**
```
2:30-3:00 | Back to chat. Type: 'Generate a dbt model...' | ...SQL displayed in Streamlit chat...
```

---

## 13. Troubleshooting Table (Line 2743)
**CHANGE:**
```
Dash page not loading | Check datamind_core is running on 8001 (frontend calls it)
```
**TO:**
```
Streamlit page not loading | Check datamind_core is running on 8001 (frontend calls it)
```

---

## Summary of File Changes Made

### Files Deleted:
- ✅ `datamind/datamind_frontend/app.py` (old Dash app)

### Files Modified:
- ✅ `datamind/README.md` - Changed "Dash UI" to "Streamlit UI"
- ✅ `datamind/README_STREAMLIT.md` - Removed Dash comparison text
- ✅ `datamind/requirements.txt` - Removed Dash dependencies
- ✅ `datamind/DEMO_GUIDE.md` - Already uses Streamlit (no changes needed)

### Files to Keep:
- ✅ `datamind/datamind_frontend/app_streamlit.py` - Current Streamlit implementation

---

## How to Update the Word Document

1. Open `DataMind_Full_Implementation.docx`
2. Use Find & Replace (Ctrl+H):
   - Find: "Dash" → Replace with: "Streamlit" (review each occurrence)
   - Find: "dash" → Replace with: "streamlit" (review each occurrence)
3. Manually update the code sections as listed above
4. Delete the three Dash page implementation sections (5.2, 5.3, 5.4)
5. Add the new Streamlit implementation section
6. Save the document

---

## Verification Checklist

After updating the document, verify:
- [ ] No mentions of "Dash" remain (except in historical context)
- [ ] All code examples use Streamlit
- [ ] All file paths reference `app_streamlit.py` not `app.py`
- [ ] All commands use `streamlit run` not `python app.py`
- [ ] Service table shows "Streamlit" not "Dash"
- [ ] Demo script references Streamlit UI
- [ ] Folder structure shows only `app_streamlit.py`

---

**Document Status:** Ready for manual update in Microsoft Word
**Last Updated:** 2026-05-22
**Changes Required:** 13 sections across the entire document