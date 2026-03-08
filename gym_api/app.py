from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
    Message,
    ResponseExerciseSchema,
    ResponseWorkoutSessionList,
    Token,
    UserPublic,
    UserSchema,
    WorkoutExerciseSchema,
    WorkoutSessionSchema,
)
from gym_api.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


@app.post('/users', response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, email=user.email, password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.put(
    '/users/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        session.commit()
        session.refresh(current_user)
        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@app.delete(
    '/users/{user_id}', response_model=Message, status_code=HTTPStatus.OK
)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='User not found',
        )
    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@app.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/exercise', response_model=ResponseExerciseSchema)
def create_exercise(
    exercise: ExerciseSchema, session: Session = Depends(get_session)
):
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


@app.get('/all-exercises', response_model=ExerciseList)
def read_exercises(session: Session = Depends(get_session)):
    all_exercises = session.scalars(select(PublicExercise)).all()
    return {'exercises': all_exercises}


@app.post('/workout-session', response_model=WorkoutSessionSchema)
def creat_workout_session(
    workout_session: WorkoutSessionSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    new_workout_session = WorkoutSession(
        user_id=current_user.id, name=workout_session.name
    )
    session.add(new_workout_session)
    session.commit()
    session.refresh(new_workout_session)

    return new_workout_session


@app.post('/workout-exercise', response_model=WorkoutExerciseSchema)
def create_workout_exercise(
    workout_exercise: WorkoutExerciseSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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


@app.get('/all-sessions', response_model=ResponseWorkoutSessionList)
def read_all_sessions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    all_sessions = session.scalars(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == current_user.id)
        .options(selectinload(WorkoutSession.exercises))
    ).all()
    return {'sessions': all_sessions}
