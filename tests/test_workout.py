from http import HTTPStatus


def test_create_exercise(client):
    response = client.post(
        '/gym/exercise',
        json={
            'name': 'Supino',
            'description': 'This is a description of the Supino exercise.',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'Supino',
        'description': 'This is a description of the Supino exercise.',
        'id': 1,
    }


def test_create_exercise_without_name(client):
    response = client.post(
        '/gym/exercise',
        json={
            'name': '',
            'description': 'This is a description of the Supino exercise.',
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Name cannot be empty'}


def test_create_exercise_already_exists(client, exercise):
    response = client.post(
        '/gym/exercise',
        json={
            'name': 'Supino',
            'description': 'This is a description of the Supino exercise.',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'This exercise already exists in database'
    }


def test_read_all_exercises(client, exercise):
    response = client.get('/gym/all-exercises')
    exercise_dict = [
        {
            'name': exercise.name,
            'description': exercise.description,
            'id': exercise.id,
        }
    ]
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'exercises': exercise_dict}


def test_create_workout_session(client, token):
    response = client.post(
        '/gym/workout-session',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Biceps Workout',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'name': 'Biceps Workout', 'exercises': []}


def test_create_workout_session_without_name(client, token):
    response = client.post(
        '/gym/workout-session',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': '',
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Name cannot be empty'}


def test_create_workout_session_without_token(client):
    response = client.post(
        '/gym/workout-session',
        json={
            'name': 'Biceps Workout',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_create_workout_session_with_invalid_token(client):
    response = client.post(
        '/gym/workout-session',
        headers={'Authorization': 'Bearer invalid-token'},
        json={
            'name': 'Biceps Workout',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_creat_workout_exercise(client, workout_session, token, exercise):
    response = client.post(
        '/gym/workout-exercise',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'session_id': workout_session.id,
            'exercise_id': exercise.id,
            'order': 1,
            'rep': 12,
            'weight': 50,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'exercise_id': 1,
        'session_id': 1,
        'order': 1,
        'rep': 12,
        'weight': 50.0,
    }


def test_creat_workout_exercise_empty_session_id(client, token, exercise):
    response = client.post(
        '/gym/workout-exercise',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'session_id': 0,
            'exercise_id': exercise.id,
            'order': 1,
            'rep': 12,
            'weight': 50,
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Session cannot be empty'}


def test_creat_workout_exercise_invalid_session_id(client, token, exercise):
    response = client.post(
        '/gym/workout-exercise',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'session_id': 999,
            'exercise_id': exercise.id,
            'order': 1,
            'rep': 12,
            'weight': 50,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Session not found'}


def test_creat_workout_exercise_invalid_exercise_id(
    client, workout_session, token
):
    response = client.post(
        '/gym/workout-exercise',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'session_id': workout_session.id,
            'exercise_id': 999,
            'order': 1,
            'rep': 12,
            'weight': 50,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Exercise not found'}


def test_read_all_sessions(
    client,
    workout_session,
    workout_exercise,
    token,
):
    response = client.get(
        'gym/all-sessions', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'sessions': [
            {
                'name': 'Biceps Workout',
                'exercises': [
                    {
                        'exercise_id': workout_exercise.id,
                        'session_id': workout_session.id,
                        'order': workout_exercise.order,
                        'rep': workout_exercise.rep,
                        'weight': workout_exercise.weight,
                    }
                ],
            }
        ]
    }
