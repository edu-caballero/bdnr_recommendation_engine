from app.domain.models import ContentSyncRequest
from app.core.neo4j_client import run_write


def sync_lesson_content(req: ContentSyncRequest) -> int:
    """
    Sincroniza relaciones estructurales de catálogo:
    - (Leccion)-[:REFUERZA_SKILL]->(Skill)
    - (Leccion)-[:TIENE_ETIQUETA]->(Etiqueta)
    - (Leccion)-[:TIENE_EJERCICIO]->(Ejercicio)

    Setea name en cada nodo:
    - Leccion.name = lesson_name (si viene) o lesson_id
    - Skill.name = id_skill (si no tenía)
    - Etiqueta.name = id_etiqueta (si no tenía)
    - Ejercicio.name = id_ejercicio (si no tenía)
    """

    cypher = """
    UNWIND $lessons AS lesson
      MERGE (l:Leccion {id_leccion: lesson.lesson_id})
        ON CREATE SET
          l.name = coalesce(lesson.lesson_name, lesson.lesson_id)
        ON MATCH SET
          l.name = coalesce(l.name, lesson.lesson_name, lesson.lesson_id)

      // Skills
      FOREACH (skill_id IN lesson.skills |
        MERGE (sk:Skill {id_skill: skill_id})
          ON CREATE SET
            sk.name = skill_id
          ON MATCH SET
            sk.name = coalesce(sk.name, skill_id)
        MERGE (l)-[:REFUERZA_SKILL]->(sk)
      )

      // Etiquetas
      FOREACH (tag_id IN lesson.tags |
        MERGE (e:Etiqueta {id_etiqueta: tag_id})
          ON CREATE SET
            e.name = tag_id
          ON MATCH SET
            e.name = coalesce(e.name, tag_id)
        MERGE (l)-[:TIENE_ETIQUETA]->(e)
      )

      // Ejercicios
      FOREACH (ex_id IN lesson.exercises |
        MERGE (ex:Ejercicio {id_ejercicio: ex_id})
          ON CREATE SET
            ex.name = ex_id
          ON MATCH SET
            ex.name = coalesce(ex.name, ex_id)
        MERGE (l)-[:TIENE_EJERCICIO]->(ex)
      )
    """

    lessons_payload = [
        {
            "lesson_id": lesson.lesson_id,
            "lesson_name": lesson.lesson_name,
            "skills": lesson.skills,
            "tags": lesson.tags,
            "exercises": lesson.exercises,
        }
        for lesson in req.lessons
    ]

    if lessons_payload:
        run_write(cypher, {"lessons": lessons_payload})

    return len(lessons_payload)
