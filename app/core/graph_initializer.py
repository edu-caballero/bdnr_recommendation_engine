from pathlib import Path
from app.core.neo4j_client import get_driver
from app.core.config import settings


# app/core/graph_initializer.py (o donde la tengas)
from pathlib import Path
from neo4j.exceptions import Neo4jError
from app.core.neo4j_client import get_driver
from app.core.config import settings


def run_cypher_file(path: Path) -> None:
    cypher = path.read_text(encoding="utf-8")
    driver = get_driver()

    print(f"[init] Ejecutando archivo Cypher: {path}...")

    with driver.session(database=settings.neo4j_database) as session:
        for idx, statement in enumerate(cypher.split(";"), start=1):
            stmt = statement.strip()
            if not stmt:
                continue

            # Mostrar los primeros caracteres para debug
            preview = " ".join(stmt.split())[:120]
            print(f"[init]  Sentencia {idx}: {preview}...")

            try:
                result = session.run(stmt)
                summary = result.consume()
                counters = summary.counters
                print(
                    f"[init]    -> nodes_created={counters.nodes_created}, "
                    f"rels_created={counters.relationships_created}, "
                    f"labels_added={counters.labels_added}, "
                    f"props_set={counters.properties_set}"
                )
            except Neo4jError as e:
                print(f"[init]    !! Error ejecutando sentencia {idx}: {e}")
                # si querés podés hacer raise acá para que reviente el startup
                # raise
    print(f"[init] Archivo {path.name} terminado.")



def initialize_graph() -> None:
    """
    Ejecuta los scripts de constraints/índices y nodos iniciales.
    Idempotente si tus .cypher usan CREATE CONSTRAINT IF NOT EXISTS, etc.
    """
    cypher_dir = settings.cypher_dir
    constraints = cypher_dir / "01_constraints_indexes.cypher"
    nodes = cypher_dir / "02_nodes.cypher"
    relations = cypher_dir / "03_relations.cypher"

    if constraints.exists():
        run_cypher_file(constraints)

    if nodes.exists():
        run_cypher_file(nodes)

    if relations.exists():
        run_cypher_file(relations)
