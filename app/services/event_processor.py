from app.domain.models import LessonCompletedEvent, UserProfile
from app.clients.profile_client import get_user_profile
from app.core.neo4j_client import run_write


def process_lesson_completed_event(event: LessonCompletedEvent) -> None:
    profile: UserProfile = get_user_profile(event.user_id)

    cypher_user_lesson = """
    MERGE (u:Usuario {id_usuario: $user_id})
      ON CREATE SET
        u.idioma = $language,
        u.nivel = $level
      ON MATCH SET
        u.idioma = coalesce(u.idioma, $language),
        u.nivel = coalesce(u.nivel, $level)

    MERGE (l:Leccion {id_leccion: $lesson_id})

    MERGE (u)-[r:COMPLETO_LECCION {fecha: date($completed_date)}]->(l)
      ON CREATE SET
        r.puntaje = $score,
        r.intentos = 1,
        r.tiempo_seg = $duration_seconds
      ON MATCH SET
        r.puntaje = $score,
        r.tiempo_seg = $duration_seconds
    """

    total = event.correct + event.incorrect
    score = (event.correct / total) * 100 if total > 0 else 0

    run_write(
        cypher_user_lesson,
        {
            "user_id": profile.user_id,
            "language": profile.language,
            "level": profile.level,
            "lesson_id": event.lesson_id,
            "completed_date": event.completed_at.date().isoformat(),
            "score": score,
            "duration_seconds": event.duration_seconds,
        },
    )

    if profile.preferences:
        cypher_prefs = """
        MERGE (u:Usuario {id_usuario: $user_id})
        WITH u, $preferences AS prefs
        UNWIND prefs AS pref
          MERGE (e:Etiqueta {id_etiqueta: pref.tag_id})
          MERGE (u)-[r:PREFIERE_ETIQUETA]->(e)
            ON CREATE SET
              r.peso = pref.weight,
              r.fuente = pref.source
            ON MATCH SET
              r.peso = pref.weight,
              r.fuente = pref.source
        """
        prefs_data = [
            {"tag_id": p.tag_id, "weight": p.weight, "source": p.source}
            for p in profile.preferences
        ]

        run_write(
            cypher_prefs,
            {
                "user_id": profile.user_id,
                "preferences": prefs_data,
            },
        )
