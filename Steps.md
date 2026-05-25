
Step 1 .env and fill your credentials
=====================================
  env: Unzip the code, create the .env, fill in your Snowflake credentials, install pip packages.

Step 2: install python dependencies 
===================================

pip install -r requirements.txt --timeout 300


Step 3 Start Neo4j with Docker
==============================


Neo4j: Start Neo4j with one Docker command, verify the browser opens at localhost:7474.

docker context use desktop-linux
docker run -d --name neo4j-datamind -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/datamind_pass neo4j:5.15

Verify Neo4j Browser opens
http://localhost:7474

Username: neo4j
Password: datamind_pass   (from your .env)

Step 4:
======
 Snowflake setup: Run the SQL worksheet to create DATAMIND_DB, the cost view, and test that Cortex Arctic responds.


Step 5:
========

add the following in the profile.yml inside the .dbt folder 

datamind_analytics:
  target: dev
  outputs:
    dev:
      type: snowflake
      account:   SE58322-FRA00296
      user:      DATAMIND_USER
      password:  DataMind@2026!
      role:      DATAMIND_ROLE
      database:  DATAMIND_DB
      warehouse: DATAMIND_WH
      schema:    DBT_DEV
      threads:   4

Step 6:
=======
      dbt compile: Add the profile to ~/.dbt/profiles.yml, run dbt compile to generate manifest.json.

Phase 7:
=========

 Ingest Neo4j: Run ingestion.py to load Snowflake tables + dbt models into Neo4j. Verify counts in the browser.

python ingestion.py ..\dbt_project\target\manifest.json

Phase 8:
=======

3 separate PowerShell windows right now and run one command in each:

1.cd C:\Users\SandipSingha\Desktop\bob-a-thon\datamind\datamind_knowledge_svc
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

2.
pip install langfuse --upgrade

cd C:\Users\SandipSingha\Desktop\bob-a-thon\datamind\datamind_core
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

3.cd C:\Users\SandipSingha\Desktop\bob-a-thon\datamind\datamind_frontend
python app.py

