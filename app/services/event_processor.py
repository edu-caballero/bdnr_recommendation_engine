from app.domain.models import (
    LessonCompletedEvent,
    UserProfile,
)
from app.clients.profile_client import get_user_profile
from app.core.neo4j_client import run_write

# --- Helpers internos --- #

def upsert_user_from_profile(profile: UserProfile) -> None:
    cypher = """
    MERGE (u:Usuario {id_usuario: $user_id})
      ON CREATE SET
        u.display_name   = $display_name,
        u.idioma         = $language,
        u.course_id      = $course_id,
        u.nivel          = $level,
        u.xp             = $xp,
        u.current_streak = $current_streak,
        u.plus_activo    = $plus_active,
        u.last_practice_at = $last_practice_at
      ON MATCH SET
        u.display_name   = coalesce(u.display_name, $display_name),
        u.idioma         = coalesce(u.idioma, $language),
        u.course_id      = coalesce(u.course_id, $course_id),
        u.nivel          = coalesce(u.nivel, $level),
        u.xp             = coalesce(u.xp, $xp),
        u.current_streak = coalesce(u.current_streak, $current_streak),
        u.plus_activo    = coalesce(u.plus_activo, $plus_active),
        u.last_practice_at = coalesce(u.last_practice_at, $last_practice_at)
    """
    run_write(
        cypher,
        {
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "language": profile.language,
            "course_id": profile.course_id,
            "level": profile.level,
            "xp": profile.xp,
            "current_streak": profile.current_streak,
            "plus_active": profile.plus_active,
            "last_practice_at": (
                profile.last_practice_at.isoformat()
                if profile.last_practice_at
                else None
            ),
        },
    )


def register_lesson_completion(profile: UserProfile, event: LessonCompletedEvent) -> None:
    cypher = """
    MERGE (u:Usuario {id_usuario: $user_id})
    MERGE (l:Leccion {id_leccion: $lesson_id})

    MERGE (u)-[r:COMPLETO_LECCION {fecha: date($completed_date)}]->(l)
      ON CREATE SET
        r.puntaje    = $score,
        r.intentos   = 1,
        r.tiempo_seg = $duration_seconds
      ON MATCH SET
        r.puntaje    = $score,
        r.tiempo_seg = $duration_seconds
    """

    total = event.correct + event.incorrect
    score = (event.correct / total) * 100 if total > 0 else 0

    run_write(
        cypher,
        {
            "user_id": profile.user_id,
            "lesson_id": event.lesson_id,
            "completed_date": event.completed_at.date().isoformat(),
            "score": score,
            "duration_seconds": event.duration_seconds,
        },
    )

def upsert_user_preferences(profile: UserProfile) -> None:
    if not profile.preferences:
        return

    cypher = """
    MERGE (u:Usuario {id_usuario: $user_id})
    WITH u, $preferences AS prefs
    UNWIND prefs AS pref
      MERGE (e:Etiqueta {id_etiqueta: pref.id})
        ON CREATE SET
          e.name = pref.id
        ON MATCH SET
          e.name = coalesce(e.name, pref.id)
      MERGE (u)-[r:PREFIERE_ETIQUETA]->(e)
        ON CREATE SET
          r.peso   = pref.weight,
          r.fuente = pref.source
        ON MATCH SET
          r.peso   = pref.weight,
          r.fuente = pref.source
    """

    prefs_data = [
        {"id": p.id, "weight": p.weight, "source": p.source}
        for p in profile.preferences
    ]

    run_write(
        cypher,
        {
            "user_id": profile.user_id,
            "preferences": prefs_data,
        },
    )

def upsert_user_skill_errors(profile: UserProfile, event: LessonCompletedEvent) -> None:
    """
    Actualiza relaciones FALLA_EN_SKILL para el usuario, en base al agregado de errores por skill.
    Upsert por (Usuario, Skill): una sola relación con los últimos valores agregados.
    """
    if not event.skills_stats:
        return

    cypher = """
    MERGE (u:Usuario {id_usuario: $user_id})
    WITH u, $skills AS skills
    UNWIND skills AS s
      MERGE (sk:Skill {id_skill: s.skill_id})
        ON CREATE SET
          sk.name = s.skill_id
        ON MATCH SET
          sk.name = coalesce(sk.name, s.skill_id)
      MERGE (u)-[r:FALLA_EN_SKILL]->(sk)
        ON CREATE SET
          r.errores   = s.errors,
          r.intentos  = s.attempts,
          r.tasa_error = CASE WHEN s.attempts > 0
                              THEN toFloat(s.errors) / s.attempts
                              ELSE 0.0 END
        ON MATCH SET
          r.errores   = s.errors,
          r.intentos  = s.attempts,
          r.tasa_error = CASE WHEN s.attempts > 0
                              THEN toFloat(s.errors) / s.attempts
                              ELSE 0.0 END
    """
    skills_payload = [
        {
            "skill_id": s.skill_id,
            "errors": s.errors,
            "attempts": s.attempts,
        }
        for s in event.skills_stats
    ]

    run_write(
        cypher,
        {
            "user_id": profile.user_id,
            "skills": skills_payload,
        },
    )


# --- Orquestador principal llamado desde el endpoint --- #

def process_lesson_completed_event(event: LessonCompletedEvent) -> None:
    """
    - Obtiene el perfil del usuario
    - Upsert del nodo Usuario
    - Registra COMPLETO_LECCION
    - Actualiza preferencias PREFIERE_ETIQUETA
    - Actualiza FALLA_EN_SKILL si el evento trae stats por skill
    """
    profile: UserProfile = get_user_profile(event.user_id)
    upsert_user_from_profile(profile)
    register_lesson_completion(profile, event)
    upsert_user_preferences(profile)
    upsert_user_skill_errors(profile, event)
