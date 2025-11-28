from fastapi import APIRouter
from app.domain.models import LessonCompletedEvent, EventIngestionResponse
from app.services.event_processor import process_lesson_completed_event

router = APIRouter(tags=["events"])


@router.post(
    "/events/lesson-completed",
    response_model=EventIngestionResponse,
)
def ingest_lesson_completed(event: LessonCompletedEvent):
    process_lesson_completed_event(event)
    return EventIngestionResponse(
        status="ok",
        message=f"Evento procesado para usuario {event.user_id}",
    )
