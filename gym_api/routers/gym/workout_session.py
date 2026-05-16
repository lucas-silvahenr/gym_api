from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_session
from gym_api.models import (
    User,
    WorkoutExercise,
    WorkoutSession,
)
from gym_api.schemas import (
    Message,
    WorkoutSessionSchema,
)
from gym_api.security import get_current_user

AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/workout-session', tags=['workout-session'])


@router.post(
    '/',
    response_model=WorkoutSessionSchema,
    status_code=HTTPStatus.CREATED,
)
async def creat_workout_session(
    workout_session: WorkoutSessionSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if not workout_session.name:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Name cannot be empty',
        )
    new_workout_session = WorkoutSession(
        user_id=current_user.id, name=workout_session.name
    )
    new_workout_session.exercises = []

    session.add(new_workout_session)
    await session.flush()

    for exercise in workout_session.exercises:
        new_workout_session.exercises.append(
            WorkoutExercise(
                session_id=new_workout_session.id,
                exercise_id=exercise.exercise_id,
                order=exercise.order,
                rep=exercise.rep,
                weight=exercise.weight,
            )
        )

    await session.commit()
    await session.refresh(new_workout_session)

    return new_workout_session


@router.put('/{workout_session_id}', response_model=Message)
async def update_workout_session(
    workout_session_id: int,
    workout_session: WorkoutSessionSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    workout_session_to_update = await session.scalar(
        select(WorkoutSession).where(
            WorkoutSession.id == workout_session_id,
            WorkoutSession.user_id == current_user.id,
        )
    )
    if not workout_session_to_update:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Workout Session not found',
        )

    workout_session_to_update.name = workout_session.name
    workout_session_to_update.exercises.clear()
    for exercise in workout_session.exercises:
        workout_session_to_update.exercises.append(
            WorkoutExercise(
                exercise_id=exercise.exercise_id,
                session_id=workout_session_to_update.id,
                order=exercise.order,
                rep=exercise.rep,
                weight=exercise.weight,
            )
        )
    await session.commit()
    await session.refresh(workout_session_to_update)
    return {'message': 'Workout Session updated'}


@router.delete('/{workout_session_id}', response_model=Message)
async def delete_workout_session(
    workout_session_id: int,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    workout_session_to_deleted = await session.scalar(
        select(WorkoutSession).where(
            WorkoutSession.id == workout_session_id,
            WorkoutSession.user_id == current_user.id,
        )
    )
    if not workout_session_to_deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Workout Session not found',
        )

    await session.delete(workout_session_to_deleted)
    await session.commit()
    return {'message': 'Workout Session deleted'}
