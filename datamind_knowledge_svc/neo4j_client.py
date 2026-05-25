from neo4j import GraphDatabase
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv("../.env")


@lru_cache
def get_driver():
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(
            os.getenv("NEO4J_USER", "neo4j"),
            os.getenv("NEO4J_PASSWORD", "datamind_pass"),
        ),
    )


def run_cypher(cypher: str, params: dict = {}) -> list[dict]:
    with get_driver().session() as s:
        result = s.run(cypher, params)
        return [dict(r) for r in result]


def create_constraints():
    stmts = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (t:SnowflakeTable)  REQUIRE (t.database, t.schema, t.name) IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (m:DbtModel)        REQUIRE m.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:SnowflakeColumn) REQUIRE (c.table, c.name) IS UNIQUE",
        "CREATE INDEX IF NOT EXISTS FOR (t:SnowflakeTable)  ON (t.schema)",
        "CREATE INDEX IF NOT EXISTS FOR (m:DbtModel)        ON (m.description)",
        "CREATE INDEX IF NOT EXISTS FOR (t:SnowflakeTable)  ON (t.name)",
    ]
    for stmt in stmts:
        try:
            run_cypher(stmt)
        except Exception as e:
            print(f"Constraint warning (may already exist): {e}")
    print("Neo4j constraints and indexes ready")
