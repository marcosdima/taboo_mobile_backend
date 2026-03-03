def test_login_success(client):
    client.post('/users', json={"alias": "marcos", "password": "123456"})

    response = client.post('/login', json={"alias": "marcos", "password": "123456"})
    body = response.get_json()

    assert response.status_code == 200
    assert "token" in body
    assert body["user"]["alias"] == "marcos"


def test_login_invalid_credentials(client):
    client.post('/users', json={"alias": "marcos", "password": "123456"})

    response = client.post('/login', json={"alias": "marcos", "password": "wrong"})
    body = response.get_json()

    assert response.status_code == 401
    assert body["error"] == "Invalid credentials"


def test_login_without_payload(client):
    response = client.post('/login', json={})
    body = response.get_json()

    assert response.status_code == 401
    assert body["error"] == "Invalid credentials"


def test_protected_route_without_token(client):
    response = client.get('/games', headers={"Authorization": ""})
    body = response.get_json()

    assert response.status_code == 401
    assert body["error"] == "Token is missing or invalid"


def test_protected_route_with_invalid_token(client):
    response = client.get('/games', headers={"Authorization": "Bearer invalid-token"})
    body = response.get_json()

    assert response.status_code == 401
    assert body["error"] == "Token is missing or invalid"
