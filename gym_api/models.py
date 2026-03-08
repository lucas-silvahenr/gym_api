from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    workout_sessions: Mapped[list['WorkoutSession']] = relationship(
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        back_populates='user',
    )


@mapped_as_dataclass(table_registry)
class PublicExercise:
    __tablename__ = 'public_exercises'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)


@mapped_as_dataclass(table_registry)
class WorkoutSession:
    __tablename__ = 'workout_sessions'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    exercises: Mapped[list['WorkoutExercise']] = relationship(
        back_populates='session',
        cascade='all, delete-orphan',
        lazy='selectin',
        order_by='WorkoutExercise.order',
        init=False,
    )

    user: Mapped['User'] = relationship(
        back_populates='workout_sessions', init=False
    )


@mapped_as_dataclass(table_registry)
class WorkoutExercise:
    __tablename__ = 'workout_exercises'
    __table_args__ = (
        UniqueConstraint(
            'session_id', 'order', name='uq_session_exercise_order'
        ),
    )
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey('workout_sessions.id'))
    exercise_id: Mapped[int] = mapped_column(ForeignKey('public_exercises.id'))
    order: Mapped[int]
    rep: Mapped[int]
    weight: Mapped[float]

    session: Mapped['WorkoutSession'] = relationship(
        back_populates='exercises', init=False
    )
    exercise: Mapped['PublicExercise'] = relationship(
        lazy='selectin', init=False
    )
