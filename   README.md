# Neo4j Recommender Service

Servicio de ejemplo para el subsistema de recomendaciones de Duolingo.

## Requisitos

- Python 3.11+
- Neo4j levantado localmente
- `01_constraints_indexes.cypher` y `02_nodes.cypher` en `cypher/`

## Instalación

```bash
pip install -r requirements.txt
cp .env.example .env
# editar .env con credenciales de Neo4j
uvicorn app.main:app --reload
