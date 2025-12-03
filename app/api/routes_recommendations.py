from fastapi import APIRouter, Query
from app.domain.models import RecommendationsResponse
from app.services.recommendation_service import recommend_for_user

router = APIRouter(tags=["recommendations"])


@router.get(
    "/users/{user_id}/recommendations",
    response_model=RecommendationsResponse,
)
def get_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    strategy: str = Query("weak-skills"),
):
    """
    Devuelve recomendaciones de lecciones/ejercicios para un usuario.
    - strategy: por ahora solo 'weak-skills'.
      Más adelante: 'similar-users', 'preferences', 'mixed'.
    """
    return recommend_for_user(user_id=user_id, strategy=strategy, limit=limit)
