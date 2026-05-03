def test_create_expense_success(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Сначала создадим машину
    car_resp = client.post("/cars/", json={
        "brand": "ExpenseCar",
        "model": "Test",
        "year": 2020,
        "license_plate": "EXP123"
    }, headers=headers)
    car_id = car_resp.json()["id"]

    expense_resp = client.post("/expenses/", json={
        "car_id": car_id,
        "date": "2026-05-01",
        "category": "ремонт",
        "amount": 5000.0,
        "description": "Замена масла"
    }, headers=headers)
    assert expense_resp.status_code == 201
    data = expense_resp.json()
    assert data["amount"] == 5000.0

def test_create_expense_car_not_found(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = client.post("/expenses/", json={
        "car_id": 9999,
        "date": "2026-05-01",
        "category": "мойка",
        "amount": 500,
        "description": ""
    }, headers=headers)
    assert resp.status_code == 404

def test_get_expenses_filter_by_car(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    # создать две машины
    car1 = client.post("/cars/", json={"brand": "A", "model": "A1", "year": 2020, "license_plate": "F1"}, headers=headers).json()
    car2 = client.post("/cars/", json={"brand": "B", "model": "B1", "year": 2021, "license_plate": "F2"}, headers=headers).json()
    client.post("/expenses/", json={"car_id": car1["id"], "date": "2026-05-01", "category": "ремонт", "amount": 100}, headers=headers)
    client.post("/expenses/", json={"car_id": car2["id"], "date": "2026-05-02", "category": "мойка", "amount": 200}, headers=headers)
    # фильтр по car1
    resp = client.get(f"/expenses/?car_id={car1['id']}", headers=headers)
    assert resp.status_code == 200
    expenses = resp.json()
    assert len(expenses) == 1
    assert expenses[0]["car_id"] == car1["id"]
