from http import HTTPStatus


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


def test_update_workout_exercise(client, token, workout_exercise, exercise):
    response = client.put(
        f'/gym/workout-exercise/{workout_exercise.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'exercise_id': exercise.id,
            'session_id': workout_exercise.session_id,
            'order': 2,
            'rep': 10,
            'weight': 25.0,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Workout Exercise updated'}


def test_update_inexistent_workout_exercise(
    client, token, workout_exercise, exercise
):
    response = client.put(
        '/gym/workout-exercise/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'exercise_id': exercise.id,
            'session_id': workout_exercise.session_id,
            'order': 2,
            'rep': 10,
            'weight': 25.0,
        },
    )

    assert response.json() == {'detail': 'Workout Exercise not found'}
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_workout_exercise(client, workout_exercise, token):
    response = client.delete(
        f'/gym/workout-exercise/{workout_exercise.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Workout Exercise deleted'}


def test_delete_inexistent_workout_exercise(client, token):
    response = client.delete(
        '/gym/workout-exercise/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Workout Exercise not found'}
