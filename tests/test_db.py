from dataclasses import asdict

import pytest
from sqlalchemy import select

from gym_api.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_time):
    with mock_time(model=User) as time:
        new_user = User(
            username='John Doe', email='johndoe@example.com', password='secret'
        )
        session.add(new_user)
        await session.commit()
    user = await session.scalar(
        select(User).where(User.username == 'John Doe')
    )

    assert asdict(user) == {
        'id': 1,
        'username': 'John Doe',
        'email': 'johndoe@example.com',
        'password': 'secret',
        'workout_sessions': [],
        'created_at': time,
    }
