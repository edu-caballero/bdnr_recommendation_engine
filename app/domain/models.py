from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class UserPreference(BaseModel):
    tag_id: str = Field(..., description="ID de la etiqueta, por ejemplo 'audio' o 'stories'")
    weight: float = Field(..., ge=0.0, le=1.0, description="Peso de preferencia")
    source: str = Field(..., description="Origen de la preferencia, por ejemplo 'explicita' o 'implicita'")


class UserProfile(BaseModel):
    user_id: str
    language: str = "en"
    level: int = 1
    preferences: List[UserPreference] = []


class LessonCompletedEvent(BaseModel):
    """
    Evento simplificado: usuario completó una lección..
    """
    user_id: str
    lesson_id: str
    correct: int = 0
    incorrect: int = 0
    duration_seconds: int = 0
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class EventIngestionResponse(BaseModel):
    status: str
    message: str
