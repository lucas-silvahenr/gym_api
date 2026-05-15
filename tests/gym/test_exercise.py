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


def test_update_exercise(client, exercise):
    response = client.put(
        f'/gym/exercise/{exercise.id}',
        json={
            'name': 'deadlift',
            'description': 'This is a deadlift description',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Exercise updated'}


def test_update_inexistent_exercise(client):
    response = client.put(
        '/gym/exercise/999',
        json={
            'name': 'deadlift',
            'description': 'This is a deadlift description',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Exercise not found'}


def test_update_exercise_without_name(client, exercise):
    response = client.put(
        f'/gym/exercise/{exercise.id}',
        json={
            'name': '',
            'description': 'This is a deadlift description',
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Name cannot be empty'}


def test_delete_exercise(client, exercise):
    response = client.delete(f'/gym/exercise/{exercise.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Exercise deleted'}


def test_delete_inexistent_exercise(client):
    response = client.delete('/gym/exercise/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Exercise not found'}


def test_read_all_exercises(client, exercise):
    response = client.get('/gym/exercise')
    exercise_dict = [
        {
            'name': exercise.name,
            'description': exercise.description,
            'id': exercise.id,
        }
    ]
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'exercises': exercise_dict}
