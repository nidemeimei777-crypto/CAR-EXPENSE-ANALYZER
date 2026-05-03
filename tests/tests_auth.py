def test_register_success(client, test_user_data):
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert "id" in data

def test_register_duplicate_email(client, test_user_data):
    client.post("/auth/register", json=test_user_data)
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "already exists" in response.text

def test_register_invalid_email(client):
    response = client.post("/auth/register", json={
        "username": "bad",
        "email": "notanemail",
        "password": "pass"
    })
    assert response.status_code == 422  # Pydantic validation

def test_login_success(client, test_user_data):
    client.post("/auth/register", json=test_user_data)
    resp = client.post("/auth/login", data={
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_wrong_password(client, test_user_data):
    client.post("/auth/register", json=test_user_data)
    resp = client.post("/auth/login", data={
        "username": test_user_data["email"],
        "password": "wrongpassword"
    })
    assert resp.status_code == 401
