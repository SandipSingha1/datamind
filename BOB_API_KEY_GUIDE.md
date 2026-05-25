# BOB_API_KEY Configuration Guide

## What is BOB_API_KEY?

The `BOB_API_KEY` in your `.env` file is an **optional security token** for authenticating requests from IBM Bob to your DataMind MCP endpoint.

---

## 🔐 Do You Need It?

### **For Local Development: NO** ❌
- If running DataMind locally (localhost:8001)
- If Bob is also running locally
- If you're just testing/demoing
- **Leave it as:** `BOB_API_KEY=your_bob_key`

### **For Production Deployment: YES** ✅
- If DataMind is deployed to a public server
- If you want to restrict access to your MCP endpoint
- If multiple users will access it
- **Set a real API key**

---

## 📝 Current Configuration

In your `datamind/.env`:
```bash
# ── IBM Bob ────────────────────────────────────────────────
BOB_API_KEY=your_bob_key
```

**This is fine for local development!** The MCP endpoint at `http://localhost:8001/mcp` will work without authentication.

---

## 🔧 How to Use BOB_API_KEY (If Needed)

### Option 1: Generate a Secure Key

```bash
# Generate a random API key
python -c "import secrets; print('bob_' + secrets.token_urlsafe(32))"
```

Example output: `bob_xK9mP2vL8nQ4wR7tY3uZ5aB6cD1eF0gH`

### Option 2: Use a Simple Key

For testing, you can use any string:
```bash
BOB_API_KEY=datamind_secret_2026
```

---

## 🔌 How Bob Uses It

When you register DataMind with Bob, you provide the MCP endpoint in `bob-config/mcp-providers.json`:

### Without Authentication (Current Setup):
```json
{
  "providers": [{
    "name": "datamind",
    "description": "DataMind: AI Data Intelligence",
    "endpoint": "http://localhost:8001/mcp",
    "tools_endpoint": "http://localhost:8001/mcp/tools",
    "auth": { "type": "none" },
    "timeout_ms": 45000
  }]
}
```

### With Authentication (If You Add It):
```json
{
  "providers": [{
    "name": "datamind",
    "description": "DataMind: AI Data Intelligence",
    "endpoint": "http://localhost:8001/mcp",
    "tools_endpoint": "http://localhost:8001/mcp/tools",
    "auth": { 
      "type": "bearer",
      "token": "your_actual_bob_api_key_here"
    },
    "timeout_ms": 45000
  }]
}
```

---

## 🚀 For Your Bob-a-thon Demo

### **Recommendation: Leave it as-is** ✅

For the Bob-a-thon demo:
1. ✅ Keep `BOB_API_KEY=your_bob_key` (placeholder is fine)
2. ✅ Use `"auth": { "type": "none" }` in Bob config
3. ✅ Focus on functionality, not security

**Why?**
- Simpler setup
- Faster demo
- No authentication errors
- Judges care about features, not security tokens

---

## 🔒 If You Want to Add Authentication

### Step 1: Update `.env`
```bash
BOB_API_KEY=datamind_secret_2026
```

### Step 2: Update `main.py` to Check the Key

Add this to `datamind_core/main.py`:

```python
from fastapi import Header, HTTPException

@app.post("/mcp")
async def mcp_handler(
    request: Request,
    authorization: str = Header(None)
):
    # Check API key
    expected_key = os.getenv("BOB_API_KEY", "")
    if expected_key and expected_key != "your_bob_key":
        if not authorization or authorization != f"Bearer {expected_key}":
            raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Rest of your existing code...
    body = await request.json()
    # ...
```

### Step 3: Update Bob Config
```json
{
  "auth": { 
    "type": "bearer",
    "token": "datamind_secret_2026"
  }
}
```

---

## 📊 Summary

| Scenario | BOB_API_KEY Value | Bob Config Auth | Notes |
|----------|-------------------|-----------------|-------|
| **Local Demo** | `your_bob_key` (placeholder) | `"type": "none"` | ✅ Recommended |
| **Local Testing** | `your_bob_key` (placeholder) | `"type": "none"` | ✅ Simple |
| **Production** | Real key (e.g., `bob_xK9m...`) | `"type": "bearer"` | ✅ Secure |
| **Public Demo** | Real key | `"type": "bearer"` | ⚠️ Optional |

---

## 🎯 For Your Current Setup

**You don't need to change anything!** 

Your current configuration:
```bash
BOB_API_KEY=your_bob_key
```

And your Bob config:
```json
"auth": { "type": "none" }
```

**This works perfectly for local development and demo!** ✅

---

## 🤔 Still Confused?

**Simple Answer:** 
- For Bob-a-thon demo: **Leave it as-is** (`your_bob_key`)
- Bob will connect without authentication
- Everything will work fine

**When to change it:**
- Only if deploying to production
- Only if you want to restrict access
- Only if judges specifically ask about security

---

**Bottom Line:** The placeholder `BOB_API_KEY=your_bob_key` is fine for your demo! Don't worry about it. 👍