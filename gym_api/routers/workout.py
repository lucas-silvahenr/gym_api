from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from gym_api.database import get_session
from gym_api.models import (
    PublicExercise,
    User,
    WorkoutExercise,
    WorkoutSession,
)
from gym_api.schemas import (
    ExerciseList,
    ExerciseSchema,
    ResponseExerciseSchema,
    ResponseWorkoutSessionList,
    WorkoutExerciseSchema,
    WorkoutSessionSchema,
)
from gym_api.security import get_current_user

router = APIRouter(prefix='/gym', tags=['gym'])

AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/exercise',
    response_model=ResponseExerciseSchema,
    status_code=HTTPStatus.CREATED,
)
async def create_exercise(exercise: ExerciseSchema, session: AnnotatedSession):
    if not exercise.name:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Name cannot be empty',
        )
    new_exercise = await session.scalar(
        select(PublicExercise).where(PublicExercise.name == exercise.name)
    )
    if new_exercise:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='This exercise already exists in database',
        )
    new_exercise = PublicExercise(
        name=exercise.name, description=exercise.description
    )
    session.add(new_exercise)
    await session.commit()
    await session.refresh(new_exercise)

    return new_exercise


@router.get('/all-exercises', response_model=ExerciseList)
async def read_exercises(session: AnnotatedSession):
    all_exercises = await session.scalars(select(PublicExercise))
    return {'exercises': all_exercises.all()}


@router.post(
    '/workout-session',
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
    session.add(new_workout_session)
    await session.commit()
    await session.refresh(new_workout_session)

    return new_workout_session


@router.post(
    '/workout-exercise',
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


@router.get('/all-sessions', response_model=ResponseWorkoutSessionList)
async def read_all_sessions(
    current_user: CurrentUser,
    session: AnnotatedSession,
):
    result = await session.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == current_user.id)
        .options(selectinload(WorkoutSession.exercises))
    )
    sessions = result.scalars().all()

    for s in sessions:
        await session.refresh(
            s, attribute_names=['exercises']
        )  # Forçar recarregamento das relações (solução provisória)

    return {'sessions': sessions}
