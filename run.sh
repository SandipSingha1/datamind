#!/bin/bash
set -e
echo "=== DataMind Startup ==="

# 1. Neo4j
echo "[1/5] Starting Neo4j..."
docker start neo4j-datamind 2>/dev/null \
  || docker run -d --name neo4j-datamind \
       -p 7474:7474 -p 7687:7687 \
       -e NEO4J_AUTH=neo4j/datamind_pass \
       neo4j:5.15
sleep 4

# 2. Compile dbt (if dbt_project exists)
if [ -d "dbt_project" ]; then
  echo "[2/5] Compiling dbt..."
  cd dbt_project && dbt compile --quiet && cd ..
else
  echo "[2/5] No dbt_project folder found — skipping dbt compile"
fi

# 3. Ingest metadata to Neo4j
echo "[3/5] Ingesting metadata to Neo4j..."
cd datamind_knowledge_svc
python ingestion.py ../dbt_project/target/manifest.json 2>/dev/null \
  || python ingestion.py
cd ..

# 4. Start knowledge service
echo "[4/5] Starting Knowledge Service on :8002..."
cd datamind_knowledge_svc
uvicorn main:app --host 0.0.0.0 --port 8002 --reload &
KNOWLEDGE_PID=$!
cd ..
sleep 3

# 5. Start core service
echo "[5/5] Starting Core Service on :8001..."
cd datamind_core
uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
CORE_PID=$!
cd ..
sleep 3

# 6. Start frontend
echo "[6/6] Starting Dash Frontend on :8050..."
cd datamind_frontend
python app.py &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "  DataMind is running!"
echo "  Dash UI:        http://localhost:8050"
echo "  Core API docs:  http://localhost:8001/docs"
echo "  Knowledge docs: http://localhost:8002/docs"
echo "  Neo4j Browser:  http://localhost:7474"
echo "=========================================="
echo "  Press Ctrl+C to stop all services"
echo ""

trap "kill $KNOWLEDGE_PID $CORE_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
