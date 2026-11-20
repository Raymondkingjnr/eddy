from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import (
    Text, DateTime, ForeignKey, String, Enum, Integer, Boolean,
    CheckConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Literal, get_args
from pgvector.sqlalchemy import Vector

LessonStatus = Literal["draft", "in_progress", "completed"]
LessonSource = Literal["manual", "ai"]
topicsStatus = Literal["not_started", "in_progress", "completed"]
# A topic body is an ordered list of sections. Lessons can be about anything
# (history, cooking, languages, programming...), so nothing here assumes code.
# "concept" = heading + prose (+ optional "Key idea" callout).
# "example" = heading + prose illustrating the concept (a worked problem, a
# case study, a sample sentence...). Any section may also carry an optional
# code block, which only programming-style lessons will use.
# Exercises live in their own table because they carry hint/solution/attempts.
SectionKind = Literal["concept", "example"]

EMBEDDING_DIM = 768


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise")
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        CheckConstraint("time_frame IS NULL OR time_frame >= 0",
                        name="ck_lessons_time_frame_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    title: Mapped[str] = mapped_column(String(225), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Total minutes. Always the SUM of its topics' time_frame; the lesson
    # service recomputes it whenever a topic is added, changed or removed.
    # 0 is valid for a draft that has no topics yet.
    time_frame: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0")

    # GUID (same type as User.id) so the FK matches on every database:
    # native UUID on Postgres, CHAR(36) on SQLite.
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False)

    status: Mapped[LessonStatus] = mapped_column(
        Enum(*get_args(LessonStatus), name="lesson_status"),
        nullable=False,
        default="draft",
    )

    # How the lesson was created (README: manual or AI-assisted).
    source: Mapped[LessonSource] = mapped_column(
        Enum(*get_args(LessonSource), name="lesson_source"),
        nullable=False,
        default="manual",
        server_default="manual",
    )

    # Set when every topic is completed.
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True)

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )

    topics: Mapped[list["Topic"]] = relationship(
        "Topic",
        back_populates="lesson",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Topic.position",
        lazy="raise",)

    notes: Mapped[list["LessonNote"]] = relationship(
        "LessonNote",
        back_populates="lesson",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="LessonNote.created_at",
        lazy="raise",)

    user: Mapped["User"] = relationship(
        "User",
        back_populates="lessons",
        lazy="raise")


class Topic(Base):
    """One step of a lesson (the left-hand 'Lesson contents' list and the
    article shown on the study screen)."""
    __tablename__ = "topics"
    __table_args__ = (
        CheckConstraint("time_frame IS NULL OR time_frame >= 0",
                        name="ck_topics_time_frame_non_negative"),
        Index("ix_topics_lesson_id_position", "lesson_id", "position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4)

    title: Mapped[str] = mapped_column(String(225), nullable=False)

    # The grey lead paragraph under the title (the topic's intro/summary).
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Estimated minutes to study this topic (shown as "TOPIC 2 · 10 MIN").
    # Includes the time of its exercises.
    time_frame: Mapped[int] = mapped_column(Integer, nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False)

    status: Mapped[topicsStatus] = mapped_column(
        Enum(*get_args(topicsStatus), name="topics_status"),
        nullable=False,
        default="not_started",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow)

    lesson: Mapped["Lesson"] = relationship(
        "Lesson",
        back_populates="topics",
        lazy="raise")

    sections: Mapped[list["TopicSection"]] = relationship(
        "TopicSection",
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TopicSection.position",
        lazy="raise")

    exercises: Mapped[list["TopicExercise"]] = relationship(
        "TopicExercise",
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TopicExercise.position",
        lazy="raise")


class TopicSection(Base):
    """An ordered content block inside a topic article, e.g.
    'Think in shapes, not loops' (concept) or
    'Example: filter model confidence' (example). Subject-agnostic: code is
    optional and only present for programming-style lessons."""
    __tablename__ = "topic_sections"
    __table_args__ = (
        Index("ix_topic_sections_topic_id_position", "topic_id", "position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    kind: Mapped[SectionKind] = mapped_column(
        Enum(*get_args(SectionKind), name="section_kind"),
        nullable=False,
        default="concept",
    )

    heading: Mapped[str] = mapped_column(String(225), nullable=False)

    # Markdown prose.
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # The highlighted "Key idea: ..." callout under a section (optional).
    key_idea: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional code block; leave both null for non-programming lessons.
    # code_language should be set whenever code is.
    code_language: Mapped[str | None] = mapped_column(
        String(30), nullable=True)
    code: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow)

    topic: Mapped["Topic"] = relationship(
        "Topic", back_populates="sections", lazy="raise")


class TopicExercise(Base):
    """The 'Quick exercise' card: prompt, optional hint, reference answer.
    Works for any subject (a question, a translation, a short write-up...)."""
    __tablename__ = "topic_exercises"
    __table_args__ = (
        CheckConstraint("time_frame >= 1",
                        name="ck_topic_exercises_time_frame_positive"),
        Index("ix_topic_exercises_topic_id_position", "topic_id", "position"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    title: Mapped[str] = mapped_column(
        String(225), nullable=False, default="Quick exercise")

    prompt: Mapped[str] = mapped_column(Text, nullable=False)

    # Revealed by "Open hint".
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reference answer / grading guide used by "Check answer" (for open-ended
    # subjects it can be a rubric rather than one exact answer).
    # Never sent to the client before an attempt.
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Minutes (the "3 MIN" pill).
    time_frame: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow)

    topic: Mapped["Topic"] = relationship(
        "Topic", back_populates="exercises", lazy="raise")

    attempts: Mapped[list["ExerciseAttempt"]] = relationship(
        "ExerciseAttempt",
        back_populates="exercise",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ExerciseAttempt.created_at",
        lazy="raise")


class ExerciseAttempt(Base):
    """One 'Check answer' submission. Owner = the lesson's owner, reached via
    exercise -> topic -> lesson (no user_id stored, so it cannot drift)."""
    __tablename__ = "exercise_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topic_exercises.id", ondelete="CASCADE"),
        nullable=False, index=True)

    answer: Mapped[str] = mapped_column(Text, nullable=False)

    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow)

    exercise: Mapped["TopicExercise"] = relationship(
        "TopicExercise", back_populates="attempts", lazy="raise")


class LessonNote(Base):
    """The 'Your notes' panel: a note captured while studying a lesson,
    optionally pinned to the topic being read."""
    __tablename__ = "lesson_notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False, index=True)

    topic_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="SET NULL"),
        nullable=True)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=utcnow, onupdate=utcnow)

    lesson: Mapped["Lesson"] = relationship(
        "Lesson", back_populates="notes", lazy="raise")
