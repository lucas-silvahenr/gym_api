from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gym_api.database import get_session
from gym_api.models import (
    PublicExercise,
    User,
)
from gym_api.schemas import (
    ExerciseList,
    ExerciseSchema,
    Message,
    ResponseExerciseSchema,
)
from gym_api.security import get_current_user

AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix='/exercise', tags=['exercise'])


@router.post(
    '/',
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


@router.get('/', response_model=ExerciseList)
async def read_exercises(session: AnnotatedSession):
    all_exercises = await session.scalars(select(PublicExercise))
    return {'exercises': all_exercises.all()}


@router.get('/{exercise_id}', response_model=ExerciseSchema)
async def read_one_exercise(session: AnnotatedSession, exercise_id: int):
    exercise = await session.scalar(
        select(PublicExercise).where(PublicExercise.id == exercise_id)
    )
    return exercise


@router.delete('/{exercise_id}', response_model=Message)
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


@router.put('/{exercise_id}', response_model=Message)
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
