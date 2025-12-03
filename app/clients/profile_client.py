from datetime import datetime, timedelta
from app.domain.models import UserProfile, UserPreference


def get_user_profile(user_id: str) -> UserProfile:
    """
    Mock del subsistema de gestión de usuarios y perfiles.
    Más adelante se puede reemplazar por una llamada HTTP a /profiles/{id}/summary-for-recommender.
    """
    if user_id == "u_101":
        return UserProfile(
            user_id="u_101",
            display_name="Edu",
            language="en",
            course_id="en_es",
            level=3,
            xp=1500,
            current_streak=12,
            last_practice_at=datetime.utcnow() - timedelta(hours=5),
            plus_active=True,
            preferences=[
                UserPreference(id="stories", weight=0.9, source="explicit"),
                UserPreference(id="audio", weight=0.7, source="implicit"),
            ],
        )

    # Perfil por defecto para otros usuarios
    return UserProfile(
        user_id=user_id,
        display_name=f"User {user_id}",
        language="es",
        course_id="es_en",
        level=1,
        xp=0,
        current_streak=0,
        last_practice_at=None,
        plus_active=False,
        preferences=[
            UserPreference(id="basics", weight=0.6, source="implicit"),
        ],
    )
