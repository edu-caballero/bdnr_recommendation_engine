from fastapi import APIRouter
from app.domain.models import (
    ContentSyncRequest,
    ContentSyncResponse,
    UserSimilaritySyncRequest,
    UserSimilaritySyncResponse,
)
from app.services.content_service import sync_lesson_content
from app.services.similarity_service import sync_user_similarity

router = APIRouter(tags=["admin"])


@router.post(
    "/admin/content-sync",
    response_model=ContentSyncResponse,
)
def content_sync(req: ContentSyncRequest):
    """
    Endpoint para que el subsistema de Lecciones y Ejercicios
    sincronice el catálogo estructural en el grafo.
    """
    count = sync_lesson_content(req)
    return ContentSyncResponse(status="ok", lessons_processed=count)


@router.post(
    "/admin/user-similarity-sync",
    response_model=UserSimilaritySyncResponse,
)
def user_similarity_sync(req: UserSimilaritySyncRequest):
    """
    Endpoint pensado para ser llamado por un job offline
    que calcula usuarios similares (por ejemplo usando una base vectorial).
    """
    count = sync_user_similarity(req)
    return UserSimilaritySyncResponse(status="ok", users_processed=count)
