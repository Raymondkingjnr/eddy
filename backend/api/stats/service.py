import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Lesson, Topic
from schemas import Stat


def compute_streak(active_days: set[date], today: date) -> int:
    """Consecutive days with at least one completed topic.

    The streak stays alive if the latest activity was today or yesterday,
    so it does not read 0 before the user has studied today.
    """
    if today in active_days:
        cursor = today
    elif (today - timedelta(days=1)) in active_days:
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while cursor in active_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


async def get_user_stats(session: AsyncSession, user_id: uuid.UUID) -> Stat:
    """Aggregate lesson/topic statistics for a single owner.

    Every query is scoped by ``user_id``. Topics are scoped through their
    owned parent lesson, never by a client-supplied identifier.
    """
    lesson_counts = await session.execute(
        select(
            func.count(Lesson.id),
            func.count(Lesson.id).filter(Lesson.status == "completed"),
            func.count(Lesson.id).filter(Lesson.status == "in_progress"),
            func.count(Lesson.id).filter(Lesson.status == "draft"),
        ).where(Lesson.user_id == user_id)
    )
    total, completed, in_progress, draft = lesson_counts.one()

    # time_spent (minutes): sum of time_frame over completed topics.
    topic_row = await session.execute(
        select(
            func.count(Topic.id),
            func.coalesce(func.sum(Topic.time_frame), 0),
        )
        .join(Lesson, Topic.lesson_id == Lesson.id)
        .where(Lesson.user_id == user_id, Topic.status == "completed")
    )
    topics_completed, time_spent = topic_row.one()

    # Distinct UTC calendar days on which the user completed a topic.
    # Computed in Python so it works on both Postgres and SQLite (SQLite has
    # no timezone() function and returns naive datetimes, stored as UTC).
    completed_rows = await session.execute(
        select(Topic.completed_at)
        .join(Lesson, Topic.lesson_id == Lesson.id)
        .where(
            Lesson.user_id == user_id,
            Topic.status == "completed",
            Topic.completed_at.is_not(None),
        )
    )
    active_days = {
        (ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None
         else ts.astimezone(timezone.utc)).date()
        for ts in completed_rows.scalars().all()
    }
    streak = compute_streak(active_days, datetime.now(timezone.utc).date())

    return Stat(
        total_lessons=total,
        completed_lessons=completed,
        in_progress_lessons=in_progress,
        draft_lessons=draft,
        topics_completed=topics_completed,
        time_spent=int(time_spent or 0),
        streak_days=streak,
    )
