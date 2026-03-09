from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from gym_api.app import app
from gym_api.database import get_session
from gym_api.models import (
    PublicExercise,
    User,
    WorkoutExercise,
    WorkoutSession,
    table_registry,
)
from gym_api.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def user(session):
    password = 'secret'
    user = User(
        username='John Doe',
        email='johndoe@example.com',
        password=get_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password
    return user


@pytest.fixture
def other_user(session):
    password = 'secret'
    other_user = User(
        username='Jane Doe',
        email='janedoe@example.com',
        password=get_password_hash(password),
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_user.clean_password = password
    return other_user


@pytest.fixture
def exercise(session):
    exercise = PublicExercise(
        name='Supino',
        description='This is a description of the Supino exercise.',
    )
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise


@pytest.fixture
def workout_session(session, user):
    workout_session = WorkoutSession(name='Biceps Workout', user_id=user.id)
    session.add(workout_session)
    session.commit()
    session.refresh(workout_session)
    return workout_session


@pytest.fixture
def workout_exercise(session, workout_session, exercise):
    workout_exercise = WorkoutExercise(
        session_id=workout_session.id,
        exercise_id=exercise.id,
        order=1,
        rep=12,
        weight=50,
    )
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    return workout_exercise


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
def mock_time():
    return _mock_db_time


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)
