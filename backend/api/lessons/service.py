import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer, selectinload

from models.models import Lesson, Topic


@dataclass(frozen=True)
class LessonProgress:
    """A lesson with progress figures computed in SQL (no topics are loaded)."""

    lesson: Lesson
    topic_count: int
    completed_topics: int
    next_topic_title: str | None
    remaining_minutes: int


async def list_lessons(
    session: AsyncSession,
    owner_id: uuid.UUID,
    skip: int = 0,
    limit: int = 20,
) -> list[LessonProgress]:
    """Return the owner's lessons, newest first, with progress figures.

    The figures come from correlated subqueries, so one query serves the whole
    page. Topics and sections are not loaded (those relationships are
    lazy="raise"), and the unused embedding column is deferred.
    """
    topic_count = (
        select(func.count(Topic.id))
        .where(Topic.lesson_id == Lesson.id)
        .correlate(Lesson)
        .scalar_subquery()
    )
    completed_topics = (
        select(func.count(Topic.id))
        .where(Topic.lesson_id == Lesson.id, Topic.status == "completed")
        .correlate(Lesson)
        .scalar_subquery()
    )
    next_topic_title = (
        select(Topic.title)
        .where(Topic.lesson_id == Lesson.id, Topic.status != "completed")
        .order_by(Topic.position, Topic.created_at)
        .limit(1)
        .correlate(Lesson)
        .scalar_subquery()
    )
    remaining_minutes = (
        select(func.coalesce(func.sum(Topic.time_frame), 0))
        .where(Topic.lesson_id == Lesson.id, Topic.status != "completed")
        .correlate(Lesson)
        .scalar_subquery()
    )
    stmt = (
        select(Lesson, topic_count, completed_topics,
               next_topic_title, remaining_minutes)
        .where(Lesson.user_id == owner_id)
        .options(defer(Lesson.embedding))
        .order_by(Lesson.created_at.desc(), Lesson.id)
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [
        LessonProgress(
            lesson=lesson,
            topic_count=total,
            completed_topics=done,
            next_topic_title=next_title,
            remaining_minutes=int(remaining),
        )
        for lesson, total, done, next_title, remaining in result.all()
    ]


async def get_lesson(
    session: AsyncSession,
    owner_id: uuid.UUID,
    lesson_id: uuid.UUID,
) -> Lesson | None:
    """Return one lesson with its topics and their sections, or None if it does
    not exist or belongs to another user (the two cases are indistinguishable).

    Exercises are not loaded: they carry reference solutions that must not be
    sent before an attempt, and no response schema exposes them yet.
    """
    stmt = (
        select(Lesson)
        .where(Lesson.id == lesson_id, Lesson.user_id == owner_id)
        .options(
            defer(Lesson.embedding),
            selectinload(Lesson.topics).options(
                defer(Topic.embedding),
                selectinload(Topic.sections),
            ),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
