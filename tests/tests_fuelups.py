def test_create_fuelup_with_expense(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Создать машину
    car_resp = client.post("/cars/", json={
        "brand": "FuelCar",
        "model": "Test",
        "year": 2022,
        "license_plate": "FUE123"
    }, headers=headers)
    car_id = car_resp.json()["id"]

    fuelup_resp = client.post("/fuelups/with_expense", json={
        "car_id": car_id,
        "date": "2026-05-02",
        "liters": 45.5,
        "price_per_liter": 60.5,
        "odometer": 10000
    }, headers=headers)
    assert fuelup_resp.status_code == 201
    result = fuelup_resp.json()
    assert "fuelup" in result
    assert "expense" in result
    # Проверка, что расход создался с категорией "заправка"
    expense_id = result["expense"]["id"]
    expense_resp = client.get(f"/expenses/", headers=headers)
    expenses = expense_resp.json()
    found = any(e["id"] == expense_id and e["category"] == "заправка" for e in expenses)
    assert found

def test_get_fuelups(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    car_resp = client.post("/cars/", json={
        "brand": "GetFuel",
        "model": "Test",
        "year": 2020,
        "license_plate": "GET123"
    }, headers=headers)
    car_id = car_resp.json()["id"]
    client.post("/fuelups/with_expense", json={"car_id": car_id, "date": "2026-05-01", "liters": 30, "price_per_liter": 70, "odometer": 5000}, headers=headers)
    resp = client.get("/fuelups/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(f["car_id"] == car_id for f in data)
