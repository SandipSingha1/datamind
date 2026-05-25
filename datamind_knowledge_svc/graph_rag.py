"""
Graph-RAG: retrieves relevant Neo4j neighbourhood context
for a set of entities, then returns it as a text string
that gets injected into agent prompts.
"""
from neo4j_client import run_cypher
from dotenv import load_dotenv

try:
    from langfuse.decorators import observe
except ImportError:
    def observe(name=None):
        def d(fn): return fn
        return d

load_dotenv("../.env")


@observe(name="graph_rag_context")
def get_graph_context(entities: list[str], query: str = "") -> str:
    """
    For each entity name (table/model), pull its immediate graph
    neighbours from Neo4j and return as a plain-text context block.
    """
    if not entities:
        return ""

    parts = []
    for name in entities[:3]:   # cap at 3 to keep tokens manageable
        rows = run_cypher("""
            MATCH (n {name:$nm})-[r]-(neighbour)
            RETURN n.name      AS src,
                   type(r)     AS rel,
                   neighbour.name AS target,
                   labels(neighbour)[0] AS tgt_type,
                   neighbour.description AS tgt_desc
            LIMIT 20
        """, {"nm": name})

        if rows:
            lines = "\n".join(
                f"  {r['src']} --[{r['rel']}]--> "
                f"{r['target']} ({r['tgt_type']})"
                + (f" — {r['tgt_desc']}" if r.get("tgt_desc") else "")
                for r in rows
            )
            parts.append(f"Graph context for '{name}':\n{lines}")

        # Also get node's own properties
        props = run_cypher("""
            MATCH (n {name:$nm})
            RETURN labels(n)[0] AS node_type,
                   n.description AS description,
                   n.materialization AS mat,
                   n.row_count AS row_count
            LIMIT 1
        """, {"nm": name})
        if props:
            p = props[0]
            summary = (
                f"  Type: {p.get('node_type','')}"
                + (f", Materialization: {p.get('mat','')}" if p.get("mat") else "")
                + (f", Rows: {p.get('row_count','')}" if p.get("row_count") else "")
                + (f", Description: {p.get('description','')}" if p.get("description") else "")
            )
            if parts:
                parts[-1] += f"\n{summary}"

    return "\n\n".join(parts)


@observe(name="explain_lineage")
def explain_lineage(
    asset_name: str,
    direction:  str = "both",
    depth:      int = 4,
) -> dict:
    depth = min(int(depth), 6)

    if direction == "upstream":
        cypher = f"""
            MATCH path = (start {{name: $nm}})
              -[:DEPENDS_ON|READS_FROM*1..{depth}]->(upstream)
            RETURN [n IN nodes(path)         | n.name]  AS chain,
                   [r IN relationships(path) | type(r)] AS rels
            LIMIT 40
        """
    elif direction == "downstream":
        cypher = f"""
            MATCH path = (upstream)
              -[:DEPENDS_ON|WRITES_TO*1..{depth}]->(start {{name: $nm}})
            RETURN [n IN nodes(path)         | n.name]  AS chain,
                   [r IN relationships(path) | type(r)] AS rels
            LIMIT 40
        """
    else:
        cypher = f"""
            MATCH path = (n {{name: $nm}})
              -[:DEPENDS_ON|READS_FROM|WRITES_TO*1..{depth}]-(related)
            RETURN [nd IN nodes(path)         | nd.name] AS chain,
                   [r  IN relationships(path) | type(r)] AS rels
            LIMIT 40
        """

    rows = run_cypher(cypher, {"nm": asset_name})
    return {
        "asset":     asset_name,
        "direction": direction,
        "depth":     depth,
        "paths":     rows,
        "count":     len(rows),
    }
