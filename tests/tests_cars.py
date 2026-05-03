def test_create_car_unauthorized(client):
    resp = client.post("/cars/", json={
        "brand": "BMW",
        "model": "X5",
        "year": 2023,
        "license_plate": "A123BC"
    })
    assert resp.status_code == 401

def test_create_car_success(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post("/cars/", json={
        "brand": "Toyota",
        "model": "Camry",
        "year": 2020,
        "license_plate": "A123BC"
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["brand"] == "Toyota"
    assert "id" in data

def test_get_cars(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Сначала создадим машину
    client.post("/cars/", json={
        "brand": "Honda",
        "model": "Civic",
        "year": 2021,
        "license_plate": "B456CD"
    }, headers=headers)
    resp = client.get("/cars/", headers=headers)
    assert resp.status_code == 200
    cars = resp.json()
    assert len(cars) >= 1
    assert any(c["brand"] == "Honda" for c in cars)

def test_update_car(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create
    create_resp = client.post("/cars/", json={
        "brand": "Ford",
        "model": "Focus",
        "year": 2019,
        "license_plate": "C789DE"
    }, headers=headers)
    car_id = create_resp.json()["id"]
    # Update
    update_resp = client.put(f"/cars/{car_id}", json={
        "brand": "Ford",
        "model": "Fusion",
        "year": 2020,
        "license_plate": "C789DE"
    }, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["model"] == "Fusion"

def test_delete_car(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    create_resp = client.post("/cars/", json={
        "brand": "Delete",
        "model": "Me",
        "year": 2022,
        "license_plate": "D123EF"
    }, headers=headers)
    car_id = create_resp.json()["id"]
    del_resp = client.delete(f"/cars/{car_id}", headers=headers)
    assert del_resp.status_code == 200
    # Verify deletion
    get_resp = client.get("/cars/", headers=headers)
    cars = get_resp.json()
    assert not any(c["id"] == car_id for c in cars)
