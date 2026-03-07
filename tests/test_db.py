from dataclasses import asdict

from sqlalchemy import select

from gym_api.models import User


def test_create_user(session, mock_time):
    with mock_time(model=User) as time:
        new_user = User(
            username='John Doe', email='johndoe@example.com', password='secret'
        )
    session.add(new_user)
    session.commit()
    user = session.scalar(select(User).where(User.username == 'John Doe'))

    assert asdict(user) == {
        'id': 1,
        'username': 'John Doe',
        'email': 'johndoe@example.com',
        'password': 'secret',
        'created_at': time,
    }
