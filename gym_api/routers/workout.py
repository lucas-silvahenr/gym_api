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
    Message,
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


@router.delete('/exercise/{exercise_id}', response_model=Message)
async def delete_exercise(exercise_id: int, session: AnnotatedSession):
    exercise_to_delete = await session.scalar(
        select(PublicExercise).where(PublicExercise.id == exercise_id)
    )
    if not exercise_to_delete:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Exercise not found'
        )
    await session.delete(exercise_to_delete)
    await session.commit()
    return {'message': 'Exercise deleted'}


@router.put('/exercise/{exercise_id}', response_model=Message)
async def update_exercise(
    exercise_id: int, session: AnnotatedSession, exercise: ExerciseSchema
):
    exercise_to_update = await session.scalar(
        select(PublicExercise).where(PublicExercise.id == exercise_id)
    )
    if not exercise_to_update:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Exercise not found'
        )

    if not exercise.name:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Name cannot be empty',
        )

    exercise_to_update.name = exercise.name
    exercise_to_update.description = exercise.description
    await session.commit()
    await session.refresh(exercise_to_update)
    return {'message': 'Exercise updated'}


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


@router.put('/workout-session/{workout_session_id}', response_model=Message)
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


@router.delete('/workout-session/{workout_session_id}', response_model=Message)
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


@router.put('/workout-exercise/{workout_exercise_id}', response_model=Message)
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


@router.delete(
    '/workout-exercise/{workout_exercise_id}', response_model=Message
)
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
