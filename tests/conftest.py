from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

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


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def user(session):
    password = 'secret'
    user = User(
        username='John Doe',
        email='johndoe@example.com',
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'secret'
    other_user = User(
        username='Jane Doe',
        email='janedoe@example.com',
        password=get_password_hash(password),
    )
    session.add(other_user)
    await session.commit()
    await session.refresh(other_user)

    other_user.clean_password = password
    return other_user


@pytest_asyncio.fixture
async def exercise(session):
    exercise = PublicExercise(
        name='Supino',
        description='This is a description of the Supino exercise.',
    )
    session.add(exercise)
    await session.commit()
    await session.refresh(exercise)
    return exercise


@pytest_asyncio.fixture
async def workout_session(session, user):
    workout_session = WorkoutSession(name='Biceps Workout', user_id=user.id)
    session.add(workout_session)
    await session.commit()
    await session.refresh(workout_session)
    return workout_session


@pytest_asyncio.fixture
async def workout_exercise(session, workout_session, exercise):
    workout_exercise = WorkoutExercise(
        session_id=workout_session.id,
        exercise_id=exercise.id,
        order=1,
        rep=12,
        weight=50,
    )
    session.add(workout_exercise)
    await session.commit()
    await session.refresh(workout_exercise)
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
