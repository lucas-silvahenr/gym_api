from http import HTTPStatus


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'John Doe',
        'email': 'johndoe@example.com',
    }


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'Richard Roe',
            'email': 'richardroe@example.com',
            'password': 'supersecret',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Richard Roe',
        'email': 'richardroe@example.com',
    }


def test_delete_user(client, user):
    response = client.delete(
        '/users/1',
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
