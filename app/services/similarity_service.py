from app.domain.models import UserSimilaritySyncRequest
from app.core.neo4j_client import run_write

def sync_user_similarity(req: UserSimilaritySyncRequest) -> int:
    """
    Actualiza relaciones SIMILAR_A para varios usuarios.
    Estrategia simple:
    - Para cada user_id, borrar relaciones SIMILAR_A salientes anteriores
    - Crear nuevas relaciones SIMILAR_A con score
    """

    for update in req.updates:
        # 1) Borrar relaciones anteriores
        cypher_delete = """
        MATCH (u:Usuario {id_usuario: $user_id})-[r:SIMILAR_A]->(:Usuario)
        DELETE r
        """
        run_write(cypher_delete, {"user_id": update.user_id})

        # 2) Crear nuevas relaciones
        if update.similar_users:
            cypher_create = """
            MATCH (u:Usuario {id_usuario: $user_id})
            WITH u, $similar_users AS sus
            UNWIND sus AS su
              MATCH (v:Usuario {id_usuario: su.id})
              MERGE (u)-[r:SIMILAR_A]->(v)
                SET r.score = su.score
            """
            sim_payload = [
                {"id": su.id, "score": su.score} for su in update.similar_users
            ]
            run_write(
                cypher_create,
                {"user_id": update.user_id, "similar_users": sim_payload},
            )

    return len(req.updates)
