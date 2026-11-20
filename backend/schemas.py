from pydantic import BaseModel, ConfigDict, field_validator
from fastapi_users import schemas

from datetime import datetime
from typing import Literal
import uuid


class UserRead(schemas.BaseUser[uuid.UUID]):
    fullname: str


class UserCreate(schemas.BaseUserCreate):
    fullname: str


class UserUpdate(schemas.BaseUserUpdate):
    fullname: str | None = None


class UserDirectoryRead(BaseModel):
    id: uuid.UUID
    fullname: str


class Stat(BaseModel):
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    draft_lessons: int
    topics_completed: int
    time_spent: int
    streak_days: int


LessonStatus = Literal["draft", "in_progress", "completed"]
TopicStatus = Literal["not_started", "in_progress", "completed"]
TopicSectionKind = Literal["concept", "example"]


class TopicSectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    position: int
    kind: TopicSectionKind
    heading: str
    body: str
    key_idea: str | None
    code_language: str | None
    code: str | None
    created_at: datetime


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    time_frame: int | None
    position: int
    status: TopicStatus
    completed_at: datetime | None
    created_at: datetime
    sections: list[TopicSectionRead]

    @field_validator("sections")
    @classmethod
    def order_sections(
        cls, sections: list[TopicSectionRead]
    ) -> list[TopicSectionRead]:
        return sorted(sections, key=lambda section: (section.position, section.created_at))


class LessonBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    time_frame: int | None
    status: LessonStatus
    created_at: datetime


class LessonSummaryRead(LessonBase):
    """Lesson fields returned by the list endpoint (no topics or sections).

    The progress fields are computed by the list query so a dashboard can render
    lesson cards without loading every topic.
    """

    topic_count: int
    completed_topics: int
    next_topic_title: str | None
    remaining_minutes: int


class LessonRead(LessonBase):
    """A single lesson with its topics (and their sections), ordered by position."""

    topics: list[TopicRead]

    @field_validator("topics")
    @classmethod
    def order_topics(cls, topics: list[TopicRead]) -> list[TopicRead]:
        return sorted(topics, key=lambda topic: (topic.position, topic.created_at))
