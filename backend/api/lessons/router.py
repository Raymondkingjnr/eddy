import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db_session
from api.users.users import current_active_user

from models.models import User
from api.lessons import service
from schemas import LessonBase, LessonRead, LessonSummaryRead

router = APIRouter(prefix="/lessons", tags=["lessons"])


def _to_summary(item: service.LessonProgress) -> LessonSummaryRead:
    return LessonSummaryRead(
        **LessonBase.model_validate(item.lesson).model_dump(),
        topic_count=item.topic_count,
        completed_topics=item.completed_topics,
        next_topic_title=item.next_topic_title,
        remaining_minutes=item.remaining_minutes,
    )


@router.get("", response_model=list[LessonSummaryRead])
async def list_lessons(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> list[LessonSummaryRead]:
    items = await service.list_lessons(session, user.id, skip=skip, limit=limit)
    return [_to_summary(item) for item in items]


@router.get("/{lesson_id}", response_model=LessonRead)
async def get_lesson(
    lesson_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
) -> LessonRead:
    lesson = await service.get_lesson(session, user.id, lesson_id)
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return LessonRead.model_validate(lesson)
