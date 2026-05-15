from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_session
from gym_api.models import (
    PublicExercise,
    User,
    WorkoutExercise,
    WorkoutSession,
)
from gym_api.schemas import (
    Message,
    WorkoutExerciseSchema,
)
from gym_api.security import get_current_user

AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/workout-exercise', tags=['workout-exercise'])


@router.post(
    '/',
    response_model=WorkoutExerciseSchema,
    status_code=HTTPStatus.CREATED,
)
async def create_workout_exercise(
    workout_exercise: WorkoutExerciseSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if not workout_exercise.session_id:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Session cannot be empty',
        )
    workout_session = await session.scalar(
        select(WorkoutSession).where(
            WorkoutSession.id == workout_exercise.session_id
        )
    )
    if not workout_session:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Session not found'
        )
    exercise = await session.scalar(
        select(PublicExercise).where(
            PublicExercise.id == workout_exercise.exercise_id
        )
    )
    if not exercise:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Exercise not found'
        )
    new_workout_exercise = WorkoutExercise(
        session_id=workout_exercise.session_id,
        exercise_id=workout_exercise.exercise_id,
        order=workout_exercise.order,
        rep=workout_exercise.rep,
        weight=workout_exercise.weight,
    )

    session.add(new_workout_exercise)
    await session.commit()
    await session.refresh(new_workout_exercise)

    return new_workout_exercise


@router.put('/{workout_exercise_id}', response_model=Message)
async def update_workout_exercise(
    workout_exercise_id: int,
    workout_exercise: WorkoutExerciseSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    workout_exercise_to_update = await session.scalar(
        select(WorkoutExercise)
        .join(WorkoutSession)
        .where(
            WorkoutExercise.id == workout_exercise_id,
            WorkoutSession.user_id == current_user.id,
        )
    )

    if not workout_exercise_to_update:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Workout Exercise not found',
        )

    workout_exercise_to_update.exercise_id = workout_exercise.exercise_id
    workout_exercise_to_update.order = workout_exercise.order
    workout_exercise_to_update.rep = workout_exercise.rep
    workout_exercise_to_update.weight = workout_exercise.weight

    await session.commit()
    await session.refresh(workout_exercise_to_update)
    return {'message': 'Workout Exercise updated'}


@router.delete('/{workout_exercise_id}', response_model=Message)
async def delete_workout_exercise(
    workout_exercise_id: int,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    workout_exercise_to_deleted = await session.scalar(
        select(WorkoutExercise)
        .join(WorkoutSession)
        .where(
            WorkoutExercise.id == workout_exercise_id,
            WorkoutSession.user_id == current_user.id,
        )
    )

    if not workout_exercise_to_deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Workout Exercise not found',
        )

    await session.delete(workout_exercise_to_deleted)
    await session.commit()

    return {'message': 'Workout Exercise deleted'}
