from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# --- Perfil de usuario (lo que devuelve el subsistema de perfiles) --- #

class UserPreference(BaseModel):
    id: str            # id de la etiqueta, ej. "stories", "audio"
    weight: float      # 0.0 - 1.0
    source: str        # "explicit" | "implicit" | lo que uses


class UserProfile(BaseModel):
    user_id: str
    display_name: str | None = None
    language: str = "en"
    course_id: str | None = None
    level: int = 1
    xp: int | None = None
    current_streak: int | None = None
    last_practice_at: datetime | None = None
    plus_active: bool = False
    preferences: List[UserPreference] = []


# --- Evento de lección completada --- #

class SkillError(BaseModel):
    skill_id: str
    errors: int = 0
    attempts: int = 0


class LessonCompletedEvent(BaseModel):
    user_id: str
    lesson_id: str
    correct: int = 0
    incorrect: int = 0
    duration_seconds: int = 0
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    skills_stats: List[SkillError] = []  # errores por skill


class EventIngestionResponse(BaseModel):
    status: str
    message: str


# --- Sincronización de catálogo (lecciones, skills, ejercicios, etiquetas) --- #

class LessonContent(BaseModel):
    lesson_id: str
    lesson_name: str | None = None
    skills: List[str] = []
    tags: List[str] = []
    exercises: List[str] = []


class ContentSyncRequest(BaseModel):
    lessons: List[LessonContent]


class ContentSyncResponse(BaseModel):
    status: str
    lessons_processed: int


# --- Similitud entre usuarios (SIMILAR_A) --- #

class SimilarUser(BaseModel):
    id: str
    score: float                  # 0.0 - 1.0


class UserSimilarityUpdate(BaseModel):
    user_id: str
    similar_users: List[SimilarUser]


class UserSimilaritySyncRequest(BaseModel):
    updates: List[UserSimilarityUpdate]


class UserSimilaritySyncResponse(BaseModel):
    status: str
    users_processed: int

class RecommendationItem(BaseModel):
    lesson_id: str
    lesson_name: Optional[str] = None
    exercise_ids: List[str] = []
    reason: str
    skills: List[str] = []
    tags: List[str] = []
    score: float
    explanation: Optional[str] = None


class RecommendationsResponse(BaseModel):
    user_id: str
    strategy: str
    items: List[RecommendationItem]