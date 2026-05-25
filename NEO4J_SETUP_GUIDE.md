# Neo4j Setup Guide for DataMind

## ⚠️ PREREQUISITE: Start Docker Desktop First!

**Before running any Docker commands, you MUST start Docker Desktop:**

1. **Open Docker Desktop** from Windows Start Menu
2. **Wait** for Docker Desktop to fully start (whale icon in system tray should be steady, not animated)
3. **Verify** Docker is running:
   ```bash
   docker --version
   docker ps
   ```

If you see "error during connect" or "cannot find file specified", Docker Desktop is not running!

---

## 🚀 Quick Start Commands

### Option 1: Start Neo4j with Docker Compose (Recommended)

```bash
# Navigate to datamind directory
cd datamind

# Start only Neo4j
docker-compose up -d neo4j

# Check if Neo4j is running
docker ps | findstr neo4j

# View Neo4j logs
docker logs neo4j-datamind

# Wait 30 seconds for Neo4j to fully start
```

### Option 2: Start All Services Together

```bash
# Navigate to datamind directory
cd datamind

# Start all services (Neo4j, Knowledge Service, Core, Frontend)
docker-compose up -d

# Check all running containers
docker ps
```

### Option 3: Start Neo4j Standalone (Without Docker Compose)

```bash
# Pull Neo4j image
docker pull neo4j:5.15

# Run Neo4j container
docker run -d `
  --name neo4j-datamind `
  -p 7474:7474 `
  -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/datamind_pass `
  -e NEO4J_PLUGINS='["apoc"]' `
  -v neo4j_data:/data `
  neo4j:5.15

# Check if running
docker ps | findstr neo4j
```

---

## 🌐 Access Neo4j Browser

Once Neo4j is running, access the browser interface:

**URL:** http://localhost:7474

**Login Credentials:**
- **Username:** `neo4j`
- **Password:** `datamind_pass`

**Connection URL:** `bolt://localhost:7687`

---

## 🔍 Verify Neo4j is Running

### Check Container Status
```bash
# PowerShell
docker ps | findstr neo4j

# Expected output:
# neo4j-datamind   neo4j:5.15   Up X minutes   0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
```

### Check Logs
```bash
docker logs neo4j-datamind

# Look for:
# "Started."
# "Remote interface available at http://localhost:7474/"
```

### Test Connection
```bash
# Using curl (if available)
curl http://localhost:7474

# Should return HTML content
```

---

## 📊 Load Data into Neo4j

### Step 1: Compile dbt Project (if not done)
```bash
cd dbt_project
dbt compile
cd ..
```

### Step 2: Ingest Metadata
```bash
cd datamind_knowledge_svc
python ingestion.py ../dbt_project/target/manifest.json
```

### Step 3: Verify Data in Neo4j Browser
1. Go to http://localhost:7474
2. Login with credentials
3. Run query:
```cypher
MATCH (n) RETURN count(n) as total_nodes
```

---

## 🛠️ Troubleshooting

### Problem: Docker Desktop Not Running ⚠️ MOST COMMON

**Error:** `error during connect: ... cannot find file specified` or `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`

**This means Docker Desktop is NOT running!**

**Solution:**
1. **Open Docker Desktop** from Windows Start Menu
2. **Wait 1-2 minutes** for it to fully start
3. **Look for whale icon** in system tray (bottom right)
4. **Icon should be steady** (not animated/spinning)
5. **Verify Docker is ready:**
   ```bash
   docker --version
   docker ps
   ```
6. **Now try again:**
   ```bash
   docker-compose up -d neo4j
   ```

### Problem: "version is obsolete" Warning

**Warning:** `the attribute 'version' is obsolete`

**This is just a warning, not an error.** Docker Compose v2 doesn't need the version field. You can ignore it or remove it from docker-compose.yml.

### Problem: Port Already in Use

**Error:** `Bind for 0.0.0.0:7474 failed: port is already allocated`

**Solution:**
```bash
# Find process using port 7474
netstat -ano | findstr :7474

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml:
# ports:
#   - "7475:7474"  # Change 7474 to 7475
#   - "7688:7687"  # Change 7687 to 7688
```

### Problem: Container Won't Start

**Solution:**
```bash
# Stop and remove existing container
docker stop neo4j-datamind
docker rm neo4j-datamind

# Remove volume (WARNING: This deletes all data)
docker volume rm datamind_neo4j_data

# Start fresh
docker-compose up -d neo4j
```

### Problem: Can't Connect to Neo4j

**Check 1: Is Neo4j running?**
```bash
docker ps | findstr neo4j
```

**Check 2: Check logs for errors**
```bash
docker logs neo4j-datamind --tail 50
```

**Check 3: Wait for startup**
```bash
# Neo4j takes 20-30 seconds to fully start
# Wait and try again
```

**Check 4: Verify credentials**
- Username: `neo4j`
- Password: `datamind_pass`

### Problem: "Database unavailable"

**Solution:**
```bash
# Restart Neo4j
docker restart neo4j-datamind

# Wait 30 seconds
timeout /t 30

# Try connecting again
```

---

## 🔧 Useful Commands

### Start/Stop Neo4j
```bash
# Start
docker start neo4j-datamind

# Stop
docker stop neo4j-datamind

# Restart
docker restart neo4j-datamind
```

### View Logs
```bash
# All logs
docker logs neo4j-datamind

# Last 50 lines
docker logs neo4j-datamind --tail 50

# Follow logs (real-time)
docker logs neo4j-datamind -f
```

### Execute Cypher Queries from Command Line
```bash
# Enter Neo4j container
docker exec -it neo4j-datamind cypher-shell -u neo4j -p datamind_pass

# Run query
MATCH (n) RETURN count(n);

# Exit
:exit
```

### Backup Neo4j Data
```bash
# Create backup
docker exec neo4j-datamind neo4j-admin database dump neo4j --to-path=/backups

# Copy backup to host
docker cp neo4j-datamind:/backups ./neo4j_backup
```

---

## 📝 Configuration Details

### Environment Variables (from docker-compose.yml)
```yaml
NEO4J_AUTH: neo4j/datamind_pass
NEO4J_PLUGINS: '["apoc"]'
```

### Ports
- **7474**: HTTP (Browser UI)
- **7687**: Bolt Protocol (Database connections)

### Volume
- **neo4j_data**: Persistent storage for database

---

## 🎯 Quick Test Queries

Once logged into Neo4j Browser (http://localhost:7474):

### 1. Count All Nodes
```cypher
MATCH (n) RETURN count(n) as total_nodes
```

### 2. Show All Node Types
```cypher
MATCH (n) RETURN DISTINCT labels(n) as node_types
```

### 3. Show Sample Nodes
```cypher
MATCH (n) RETURN n LIMIT 25
```

### 4. Find dbt Models
```cypher
MATCH (n:DbtModel) RETURN n.name, n.description LIMIT 10
```

### 5. Show Lineage for a Table
```cypher
MATCH path = (n {name: 'fct_orders'})-[*1..3]-(related)
RETURN path
LIMIT 50
```

---

## 🔗 Integration with DataMind

### Knowledge Service Connection
The Knowledge Service connects to Neo4j using:
- **URI:** `bolt://localhost:7687` (from .env file)
- **Username:** `neo4j`
- **Password:** `datamind_pass`

### Test Knowledge Service
```bash
# Start Knowledge Service
cd datamind_knowledge_svc
uvicorn main:app --host 0.0.0.0 --port 8002

# Test lineage endpoint
curl -X POST http://localhost:8002/lineage/explain `
  -H "Content-Type: application/json" `
  -d '{"asset_name": "fct_orders", "direction": "both", "depth": 4}'
```

---

## 📚 Additional Resources

- **Neo4j Documentation:** https://neo4j.com/docs/
- **Cypher Query Language:** https://neo4j.com/docs/cypher-manual/
- **APOC Procedures:** https://neo4j.com/labs/apoc/
- **Neo4j Browser Guide:** https://neo4j.com/docs/browser-manual/

---

## ✅ Success Checklist

- [ ] Neo4j container is running (`docker ps`)
- [ ] Can access Neo4j Browser at http://localhost:7474
- [ ] Can login with neo4j/datamind_pass
- [ ] Database shows nodes (run `MATCH (n) RETURN count(n)`)
- [ ] Knowledge Service can connect (check logs)
- [ ] Lineage queries work in DataMind frontend

---

**Need Help?**
- Check logs: `docker logs neo4j-datamind`
- Restart: `docker restart neo4j-datamind`
- Fresh start: `docker-compose down && docker-compose up -d`

**Status Check:**
```bash
# Quick status check
docker ps | findstr neo4j && echo "✅ Neo4j is running" || echo "❌ Neo4j is not running"