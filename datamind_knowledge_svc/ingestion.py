"""
Run this after every `dbt compile` to keep Neo4j in sync with
your Snowflake + dbt metadata.

Usage:
    python ingestion.py                                    # default manifest path
    python ingestion.py ../dbt_project/target/manifest.json
"""
import snowflake.connector
import json, os, sys
from dotenv import load_dotenv
from neo4j_client import run_cypher, create_constraints

load_dotenv("../.env")


def sf_conn():
    return snowflake.connector.connect(
        account   = os.getenv("SF_ACCOUNT"),
        user      = os.getenv("SF_USER"),
        password  = os.getenv("SF_PASSWORD"),
        warehouse = os.getenv("SF_WAREHOUSE", "COMPUTE_WH"),
        database  = os.getenv("SF_DATABASE", "DATAMIND_DB"),
        schema    = os.getenv("SF_SCHEMA", "PUBLIC"),
    )


def ingest_tables(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE,
               COALESCE(ROW_COUNT,0), COALESCE(BYTES,0), COALESCE(COMMENT,'')
        FROM   INFORMATION_SCHEMA.TABLES
        WHERE  TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA')
    """)
    count = 0
    for row in cur.fetchall():
        run_cypher("""
            MERGE (t:SnowflakeTable {database:$db, schema:$sc, name:$nm})
            SET t.type=$tp, t.row_count=$rc, t.bytes=$by, t.comment=$cm
        """, {"db":row[0],"sc":row[1],"nm":row[2],
              "tp":row[3],"rc":row[4],"by":row[5],"cm":row[6]})
        count += 1
    print(f"  Tables ingested: {count}")


def ingest_columns(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME,
               COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COALESCE(COMMENT,'')
        FROM   INFORMATION_SCHEMA.COLUMNS
        WHERE  TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA')
        ORDER  BY TABLE_NAME, ORDINAL_POSITION
    """)
    count = 0
    for row in cur.fetchall():
        run_cypher("""
            MATCH  (t:SnowflakeTable {database:$db, schema:$sc, name:$tnm})
            MERGE  (c:SnowflakeColumn {table:$tnm, name:$cnm})
            SET    c.data_type=$dt, c.nullable=$nl, c.comment=$cm
            MERGE  (t)-[:HAS_COLUMN]->(c)
        """, {"db":row[0],"sc":row[1],"tnm":row[2],
              "cnm":row[3],"dt":row[4],"nl":row[5],"cm":row[6]})
        count += 1
    print(f"  Columns ingested: {count}")


def ingest_dbt(manifest_path: str):
    if not os.path.exists(manifest_path):
        print(f"  Manifest not found at {manifest_path} — run 'dbt compile' first")
        return
    manifest = json.load(open(manifest_path))
    model_count = dep_count = 0
    for node_id, node in manifest.get("nodes", {}).items():
        if node["resource_type"] != "model":
            continue
        run_cypher("""
            MERGE (m:DbtModel {name:$nm})
            SET m.path=$path, m.materialization=$mat,
                m.description=$desc, m.schema=$sc
        """, {
            "nm":   node["name"],
            "path": node.get("original_file_path", ""),
            "mat":  node.get("config", {}).get("materialized", "table"),
            "desc": node.get("description", ""),
            "sc":   node.get("schema", ""),
        })
        model_count += 1
        for dep in node.get("depends_on", {}).get("nodes", []):
            dep_name = dep.split(".")[-1]
            run_cypher("""
                MATCH (m:DbtModel {name:$nm})
                MERGE (d:DbtModel {name:$dep})
                MERGE (m)-[:DEPENDS_ON]->(d)
            """, {"nm": node["name"], "dep": dep_name})
            dep_count += 1
    print(f"  dbt models ingested: {model_count}, dependencies: {dep_count}")


if __name__ == "__main__":
    manifest = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "../dbt_project/target/manifest.json"
    )
    print("Starting DataMind metadata ingestion...")
    create_constraints()
    conn = sf_conn()
    ingest_tables(conn)
    ingest_columns(conn)
    ingest_dbt(manifest)
    conn.close()
    print("Ingestion complete!")
