"""add time_frame to lessons and topics

Revision ID: bf7394f712cd
Revises: 23a10647eb22
Create Date: 2026-11-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bf7394f712cd"
down_revision: Union[str, Sequence[str], None] = "23a10647eb22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lessons", sa.Column("time_frame", sa.Integer(), nullable=True))
    op.add_column("topics", sa.Column("time_frame", sa.Integer(), nullable=True))
    # batch_alter_table is a plain ALTER on Postgres and a table rebuild on
    # SQLite (which can't add constraints to an existing table).
    with op.batch_alter_table("lessons") as batch_op:
        batch_op.create_check_constraint(
            "ck_lessons_time_frame_non_negative",
            "time_frame IS NULL OR time_frame >= 0",
        )
    with op.batch_alter_table("topics") as batch_op:
        batch_op.create_check_constraint(
            "ck_topics_time_frame_non_negative",
            "time_frame IS NULL OR time_frame >= 0",
        )


def downgrade() -> None:
    with op.batch_alter_table("topics") as batch_op:
        batch_op.drop_constraint("ck_topics_time_frame_non_negative", type_="check")
        batch_op.drop_column("time_frame")
    with op.batch_alter_table("lessons") as batch_op:
        batch_op.drop_constraint("ck_lessons_time_frame_non_negative", type_="check")
        batch_op.drop_column("time_frame")
