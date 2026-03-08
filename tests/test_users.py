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


def test_create_user_email_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'John Doel',
            'email': 'johndoe@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_create_user_username_already_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'John Doe',
            'email': 'johndoel@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_invalid_email(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'John Doel',
            'email': '',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['loc'][-1] == 'email'


def test_create_user_invalid_password(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'John Doel',
            'email': 'johndoel@example.com',
            'password': '',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Password cannot be empty'}


def test_create_user_invalid_username(client, user):
    response = client.post(
        '/users/',
        json={
            'username': '',
            'email': 'johndoel@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Username cannot be empty'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
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


def test_update_user_wrong_user_id(client, user, other_user, token):

    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Richard Roe',
            'email': 'richardroe@example.com',
            'password': 'supersecret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_already_exists(client, user, other_user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Jane Doe',
            'email': 'janedoe@example.com',
            'password': 'supersecret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_update_user_without_token(client, user):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'Richard Roe',
            'email': 'richardroe@example.com',
            'password': 'supersecret',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_user_with_invalid_token(client, user):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': 'Bearer invalid-token'},
        json={
            'username': 'Richard Roe',
            'email': 'richardroe@example.com',
            'password': 'supersecret',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_update_non_existent_user(client, user, token):
    response = client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Richard Roe',
            'email': 'richardroe@example.com',
            'password': 'supersecret',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_found(client, user, token):
    response = client.delete(
        '/users/999', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_without_token(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_delete_user_with_invalid_token(client, user):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_user_wrong_user(client, user, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You do not have permission to delete this user'
    }
