from typing import List
from app.core.neo4j_client import run_read
from app.domain.models import RecommendationItem, RecommendationsResponse


# -------------------------
# Estrategia 1: weak-skills
# -------------------------

def recommend_by_weak_skills(
    user_id: str,
    limit: int = 10,
    min_error_rate: float = 0.3,
) -> List[RecommendationItem]:
    """
    Estrategia 1: refuerzo de skills débiles.
    - Busca skills con tasa_error alta para el usuario.
    - Encuentra lecciones que refuercen esas skills.
    - Evita lecciones ya completadas por el usuario.
    """

    cypher = """
    MATCH (u:Usuario {id_usuario: $user_id})-[fs:FALLA_EN_SKILL]->(sk:Skill)
    WHERE fs.tasa_error >= $min_error_rate
    WITH u, sk, fs
    MATCH (sk)<-[:REFUERZA_SKILL]-(l:Leccion)
    WHERE NOT EXISTS( (u)-[:COMPLETO_LECCION]->(l) )
    OPTIONAL MATCH (l)-[:TIENE_EJERCICIO]->(e:Ejercicio)
    OPTIONAL MATCH (l)-[:TIENE_ETIQUETA]->(tag:Etiqueta)
    WITH
      l,
      collect(DISTINCT e.id_ejercicio)      AS exercise_ids,
      collect(DISTINCT sk.id_skill)         AS skills_ids,
      collect(DISTINCT tag.id_etiqueta)     AS tag_ids,
      max(fs.tasa_error)                    AS skill_score
    RETURN
      l.id_leccion AS lesson_id,
      l.name       AS lesson_name,
      exercise_ids,
      skills_ids,
      tag_ids,
      skill_score AS score
    ORDER BY score DESC
    LIMIT $limit
    """

    rows = run_read(
        cypher,
        {
            "user_id": user_id,
            "min_error_rate": min_error_rate,
            "limit": limit,
        },
    )

    items: List[RecommendationItem] = []
    for row in rows:
        explanation = (
            f"Refuerza skills débiles ({', '.join(row['skills_ids'])}) "
            f"con tasa de error aproximada {row['score']:.2f}."
        )
        items.append(
            RecommendationItem(
                lesson_id=row["lesson_id"],
                lesson_name=row.get("lesson_name"),
                exercise_ids=row.get("exercise_ids") or [],
                skills=row.get("skills_ids") or [],
                tags=row.get("tag_ids") or [],
                score=row["score"],
                reason="refuerzo_de_skill",
                explanation=explanation,
            )
        )

    return items


# -----------------------------
# Estrategia 2: similar-users
# -----------------------------

def recommend_by_similar_users(
    user_id: str,
    limit: int = 10,
) -> List[RecommendationItem]:
    """
    Estrategia 2: usuarios similares.
    - Parte de (u)-[:SIMILAR_A]->(v).
    - Toma lecciones que v haya completado y u todavía no.
    - Pondera por score de similitud (sum de sim.score).
    """

    cypher = """
    MATCH (u:Usuario {id_usuario: $user_id})-[sim:SIMILAR_A]->(v:Usuario)
    MATCH (v)-[:COMPLETO_LECCION]->(l:Leccion)
    WHERE NOT EXISTS( (u)-[:COMPLETO_LECCION]->(l) )
    OPTIONAL MATCH (l)-[:TIENE_EJERCICIO]->(e:Ejercicio)
    OPTIONAL MATCH (l)-[:TIENE_ETIQUETA]->(tag:Etiqueta)
    WITH
      l,
      collect(DISTINCT e.id_ejercicio)     AS exercise_ids,
      collect(DISTINCT tag.id_etiqueta)    AS tag_ids,
      collect(DISTINCT sim.score)          AS sim_scores
    WITH
      l,
      exercise_ids,
      tag_ids,
      // score = suma de similitudes de los vecinos que completaron la lección
      reduce(s = 0.0, sc IN sim_scores | s + sc) AS score
    RETURN
      l.id_leccion AS lesson_id,
      l.name       AS lesson_name,
      exercise_ids,
      tag_ids,
      score
    ORDER BY score DESC
    LIMIT $limit
    """

    rows = run_read(
        cypher,
        {
            "user_id": user_id,
            "limit": limit,
        },
    )

    items: List[RecommendationItem] = []
    for row in rows:
        explanation = (
            f"Lecciones completadas por usuarios similares, "
            f"score acumulado de similitud {row['score']:.2f}."
        )
        items.append(
            RecommendationItem(
                lesson_id=row["lesson_id"],
                lesson_name=row.get("lesson_name"),
                exercise_ids=row.get("exercise_ids") or [],
                skills=[],  # podrías enriquecer con REFUERZA_SKILL si quisieras
                tags=row.get("tag_ids") or [],
                score=row["score"],
                reason="usuarios_similares",
                explanation=explanation,
            )
        )

    return items


# ----------------------------------------------------
# Estrategia 3: FALLA_EN_SKILL + PREFIERE_ETIQUETA
# ----------------------------------------------------

def recommend_by_skills_and_preferences(
    user_id: str,
    limit: int = 10,
    min_error_rate: float = 0.3,
    alpha: float = 0.7,   # peso de las skills débiles
    beta: float = 0.3,    # peso de las preferencias de contenido
) -> List[RecommendationItem]:
    """
    Estrategia 3: combina skills débiles + preferencias de contenido.
    - Empezamos por FALLA_EN_SKILL.
    - Buscamos lecciones que REFUERZA_SKILL esas skills.
    - Incorporamos PREFIERE_ETIQUETA del usuario sobre las etiquetas de esas lecciones.
    - score = alpha * skill_score + beta * pref_score
    """

    cypher = """
    MATCH (u:Usuario {id_usuario: $user_id})-[fs:FALLA_EN_SKILL]->(sk:Skill)
    WHERE fs.tasa_error >= $min_error_rate
    MATCH (sk)<-[:REFUERZA_SKILL]-(l:Leccion)
    WHERE NOT EXISTS( (u)-[:COMPLETO_LECCION]->(l) )
    OPTIONAL MATCH (l)-[:TIENE_EJERCICIO]->(e:Ejercicio)
    OPTIONAL MATCH (l)-[:TIENE_ETIQUETA]->(t:Etiqueta)
    OPTIONAL MATCH (u)-[p:PREFIERE_ETIQUETA]->(t)
    WITH
      l,
      collect(DISTINCT e.id_ejercicio)     AS exercise_ids,
      collect(DISTINCT sk.id_skill)        AS skills_ids,
      collect(DISTINCT t.id_etiqueta)      AS tag_ids,
      max(fs.tasa_error)                   AS skill_score,
      sum(coalesce(p.peso, 0.0))           AS pref_score
    WITH
      l,
      exercise_ids,
      skills_ids,
      tag_ids,
      skill_score,
      pref_score,
      (skill_score * $alpha + pref_score * $beta) AS score
    RETURN
      l.id_leccion AS lesson_id,
      l.name       AS lesson_name,
      exercise_ids,
      skills_ids,
      tag_ids,
      skill_score,
      pref_score,
      score
    ORDER BY score DESC
    LIMIT $limit
    """

    rows = run_read(
        cypher,
        {
            "user_id": user_id,
            "min_error_rate": min_error_rate,
            "alpha": alpha,
            "beta": beta,
            "limit": limit,
        },
    )

    items: List[RecommendationItem] = []
    for row in rows:
        explanation = (
            f"Refuerza skills débiles ({', '.join(row['skills_ids'])}) "
            f"y respeta tus preferencias de contenido "
            f"(tags: {', '.join(row['tag_ids'] or [])}). "
            f"Skill_score={row['skill_score']:.2f}, "
            f"pref_score={row['pref_score']:.2f}."
        )
        items.append(
            RecommendationItem(
                lesson_id=row["lesson_id"],
                lesson_name=row.get("lesson_name"),
                exercise_ids=row.get("exercise_ids") or [],
                skills=row.get("skills_ids") or [],
                tags=row.get("tag_ids") or [],
                score=row["score"],
                reason="skills_y_preferencias",
                explanation=explanation,
            )
        )

    return items


# ----------------------------------------
# Orquestador: decide qué estrategia usar
# ----------------------------------------

def recommend_for_user(
    user_id: str,
    strategy: str = "weak-skills",
    limit: int = 10,
) -> RecommendationsResponse:
    """
    Orquestador de estrategias.
    - 'weak-skills'            -> FALLA_EN_SKILL
    - 'similar-users'          -> SIMILAR_A + COMPLETO_LECCION
    - 'skills-and-preferences' -> FALLA_EN_SKILL + PREFIERE_ETIQUETA
    - cualquier otro valor     -> fallback a 'weak-skills'
    """
    strategy_used = strategy

    if strategy == "weak-skills":
        items = recommend_by_weak_skills(user_id, limit)
    elif strategy == "similar-users":
        items = recommend_by_similar_users(user_id, limit)
    elif strategy in ("skills-and-preferences", "skills_y_preferencias"):
        items = recommend_by_skills_and_preferences(user_id, limit)
        strategy_used = "skills-and-preferences"
    else:
        strategy_used = "weak-skills"
        items = recommend_by_weak_skills(user_id, limit)

    return RecommendationsResponse(
        user_id=user_id,
        strategy=strategy_used,
        items=items,
    )
