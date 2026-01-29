"""Add due_datetime, recurrence_rule, and recurrence_parent_id to tasks table.

Revision ID: 002_add_due_datetime_and_recurrence
Revises: 001_initial  # Assume previous revision
Create Date: 2026-01-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_add_due_datetime_and_recurrence'
down_revision = '001_initial'  # Adjust if different
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename due_date to due_datetime and make nullable, change to timestamptz
    op.alter_column('tasks', 'due_date',
                    existing_type=sa.TIMESTAMP(),
                    type_=sa.TIMESTAMP(timezone=True),
                    existing_nullable=False,
                    nullable=True,
                    new_column_name='due_datetime')

    # Add recurrence_rule
    op.add_column('tasks', sa.Column(
        'recurrence_rule', sa.String(length=20), nullable=True
    ))
    op.execute("ALTER TABLE tasks ADD CONSTRAINT chk_recurrence_rule CHECK (recurrence_rule IN ('daily', 'weekly', 'monthly', 'yearly'))")

    # Add recurrence_parent_id
    op.add_column('tasks', sa.Column(
        'recurrence_parent_id', sa.Integer(), nullable=True
    ))
    op.create_foreign_key(None, 'tasks', 'tasks', ['recurrence_parent_id'], ['id'], ondelete='SET NULL')

    # Add indexes
    op.create_index('ix_tasks_due_datetime', 'tasks', ['due_datetime'], unique=False)
    op.create_index('ix_tasks_recurrence_rule', 'tasks', ['recurrence_rule'], unique=False)
    op.create_index('ix_tasks_recurrence_parent_id', 'tasks', ['recurrence_parent_id'], unique=False)
    op.create_index('ix_tasks_owner_due_status', 'tasks', ['owner_id', 'due_datetime', 'status'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_tasks_owner_due_status', table_name='tasks')
    op.drop_index('ix_tasks_recurrence_parent_id', table_name='tasks')
    op.drop_index('ix_tasks_recurrence_rule', table_name='tasks')
    op.drop_index('ix_tasks_due_datetime', table_name='tasks')

    # Drop FK
    op.drop_constraint(None, 'tasks', type_='foreignkey')  # recurrence_parent_id FK

    # Drop columns
    op.drop_column('tasks', 'recurrence_parent_id')
    op.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_recurrence_rule")
    op.drop_column('tasks', 'recurrence_rule')

    # Rename back due_datetime to due_date and make non-nullable (caution: data loss if nulls exist)
    op.alter_column('tasks', 'due_datetime',
                    existing_type=sa.TIMESTAMP(timezone=True),
                    type_=sa.TIMESTAMP(),
                    existing_nullable=True,
                    nullable=False,
                    new_column_name='due_date')