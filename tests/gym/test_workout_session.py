from http import HTTPStatus


def test_create_empty_workout_session(client, token):
    response = client.post(
        '/gym/workout-session',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Biceps Workout',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'name': 'Biceps Workout', 'exercises': []}


def test_create_workout_session_with_exercises(
    client, token, workout_exercise
):
    response = client.post(
        '/gym/workout-session',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Biceps Workout',
            'exercises': [
                {
                    'exercise_id': workout_exercise.id,
                    'order': workout_exercise.order,
                    'rep': workout_exercise.rep,
                    'weight': workout_exercise.weight,
                }
            ],
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'Biceps Workout',
        'exercises': [
            {
                'exercise_id': workout_exercise.id,
                'order': workout_exercise.order,
                'rep': workout_exercise.rep,
                'weight': workout_exercise.weight,
            }
        ],
    }


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


def test_delete_workout_session(client, workout_session, token):
    response = client.delete(
        f'/gym/workout-session/{workout_session.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Workout Session deleted'}


def test_delete_inexistent_workout_session(client, token):
    response = client.delete(
        '/gym/workout-session/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Workout Session not found'}


def test_update_workout_session(client, token, workout_session, exercise):
    response = client.put(
        f'/gym/workout-session/{workout_session.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'ABC',
            'exercises': [
                {
                    'exercise_id': exercise.id,
                    'session_id': workout_session.id,
                    'order': 2,
                    'rep': 10,
                    'weight': 25.0,
                }
            ],
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Workout Session updated'}


def test_update_inexistent_workout_session(
    client, token, workout_session, exercise
):
    response = client.put(
        '/gym/workout-session/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'ABC',
            'exercises': [
                {
                    'exercise_id': exercise.id,
                    'session_id': workout_session.id,
                    'order': 2,
                    'rep': 10,
                    'weight': 25.0,
                }
            ],
        },
    )

    assert response.json() == {'detail': 'Workout Session not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_read_all_sessions(
    client,
    workout_session,
    workout_exercise,
    token,
):
    response = client.get(
        'gym/sessions', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'sessions': [
            {
                'name': 'Biceps Workout',
                'exercises': [
                    {
                        'exercise_id': workout_exercise.id,
                        'order': workout_exercise.order,
                        'rep': workout_exercise.rep,
                        'weight': workout_exercise.weight,
                    }
                ],
            }
        ]
    }
