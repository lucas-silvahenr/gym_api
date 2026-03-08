from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

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

AnnotatedSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/exercise', response_model=ResponseExerciseSchema)
def create_exercise(exercise: ExerciseSchema, session: AnnotatedSession):
    new_exercise = session.scalar(
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
    session.commit()
    session.refresh(new_exercise)

    return new_exercise


@router.get('/all-exercises', response_model=ExerciseList)
def read_exercises(session: AnnotatedSession):
    all_exercises = session.scalars(select(PublicExercise)).all()
    return {'exercises': all_exercises}


@router.post('/workout-session', response_model=WorkoutSessionSchema)
def creat_workout_session(
    workout_session: WorkoutSessionSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    new_workout_session = WorkoutSession(
        user_id=current_user.id, name=workout_session.name
    )
    session.add(new_workout_session)
    session.commit()
    session.refresh(new_workout_session)

    return new_workout_session


@router.post('/workout-exercise', response_model=WorkoutExerciseSchema)
def create_workout_exercise(
    workout_exercise: WorkoutExerciseSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if not workout_exercise.session_id:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Session does not exist'
        )

    new_workout_exercise = WorkoutExercise(
        session_id=workout_exercise.session_id,
        exercise_id=workout_exercise.exercise_id,
        order=workout_exercise.order,
        rep=workout_exercise.rep,
        weight=workout_exercise.weight,
    )

    session.add(new_workout_exercise)
    session.commit()
    session.refresh(new_workout_exercise)

    return new_workout_exercise


@router.get('/all-sessions', response_model=ResponseWorkoutSessionList)
def read_all_sessions(
    current_user: CurrentUser,
    session: AnnotatedSession,
):
    all_sessions = session.scalars(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == current_user.id)
        .options(selectinload(WorkoutSession.exercises))
    ).all()
    return {'sessions': all_sessions}
