from app.domain.models import UserProfile, UserPreference


def get_user_profile(user_id: str) -> UserProfile:
    """
    Mock del subsistema de gestión de usuarios y perfiles.
    Ahora devuelve datos estáticos; en el futuro puede ir contra Mongo o un API real.
    """
    if user_id == "u_101":
        return UserProfile(
            user_id="u_101",
            language="en",
            level=3,
            preferences=[
                UserPreference(tag_id="stories", weight=0.9, source="explicita"),
                UserPreference(tag_id="audio", weight=0.7, source="implicita"),
            ],
        )
    else:
        # Perfil por defecto
        return UserProfile(
            user_id=user_id,
            language="es",
            level=1,
            preferences=[
                UserPreference(tag_id="basics", weight=0.6, source="implicita"),
            ],
        )
