from fastapi import Body

example_create_car = Body(
    openapi_examples={
        "normal": {
            "summary": "Типовой запрос",
            "description": "Создание автомобиля с заполненными полями",
            "value": {
                "brand": "Toyota",
                "model": "Camry",
                "year": 2022,
                "license_plate": "А123ВС190",
            },
        },
        "old_car": {
            "summary": "Старый автомобиль",
            "description": "Создание автомобиля старого года выпуска",
            "value": {
                "brand": "ВАЗ",
                "model": "2107",
                "year": 1995,
                "license_plate": "Х987ОХ77",
            },
        },
        "invalid_year": {
            "summary": "Некорректный год",
            "description": "Год выпуска не может быть в будущем",
            "value": {
                "brand": "Tesla",
                "model": "Cybertruck",
                "year": 2030,
                "license_plate": "Е123ЕЕ62",
            },
        },
    }
)

example_create_fuelup = Body(
    openapi_examples={
        "normal": {
            "summary": "Типовая заправка",
            "description": "Заправка полного бака",
            "value": {
                "car_id": 1,
                "date": "2024-04-15",
                "liters": 45.5,
                "price_per_liter": 52.30,
                "odometer": 15200,
            },
        },
        "partial": {
            "summary": "Частичная заправка",
            "description": "Заправка не до полного бака",
            "value": {
                "car_id": 1,
                "date": "2024-04-20",
                "liters": 20.0,
                "price_per_liter": 53.10,
                "odometer": 15600,
            },
        },
        "invalid_car": {
            "summary": "Несуществующий автомобиль",
            "description": "Указан car_id, которого нет в базе, вернётся ошибка 404",
            "value": {
                "car_id": 999,
                "date": "2024-04-25",
                "liters": 40.0,
                "price_per_liter": 54.20,
                "odometer": 16000,
            },
        },
    }
)

example_create_expense = Body(
    openapi_examples={
        "repair": {
            "summary": "Ремонт автомобиля",
            "description": "Запись о расходах на ремонт",
            "value": {
                "car_id": 1,
                "date": "2024-04-10",
                "category": "repair",
                "amount": 12500.00,
                "description": "Замена масла и фильтров",
            },
        },
        "insurance": {
            "summary": "Страховка",
            "description": "Оформление страхового полиса",
            "value": {
                "car_id": 1,
                "date": "2024-03-01",
                "category": "insurance",
                "amount": 8500.00,
                "description": "ОСАГО",
            },
        },
        "wash": {
            "summary": "Мойка",
            "description": "Расходы на автомойку",
            "value": {
                "car_id": 1,
                "date": "2024-04-18",
                "category": "wash",
                "amount": 500.00,
                "description": "Мойка кузова",
            },
        },
    }
)

example_create_reminder = Body(
    openapi_examples={
        "oil_change": {
            "summary": "Замена масла",
            "description": "Напоминание о плановой замене масла",
            "value": {
                "car_id": 1,
                "due_date": "2024-05-15",
                "title": "Замена масла и фильтров",
                "description": "Пробег после последней замены: 15000 км",
                "triggered_at_odometer": 15000,
            },
        },
        "tire_change": {
            "summary": "Сезонная смена шин",
            "description": "Напоминание о смене резины",
            "value": {
                "car_id": 1,
                "due_date": "2024-10-15",
                "title": "Смена шин на зимние",
                "description": "Температура ниже +5°C",
                "triggered_at_odometer": None,
            },
        },
    }
)


example_register_user = Body(
    openapi_examples={
        "normal": {
            "summary": "Типовая регистрация",
            "description": "Регистрация нового пользователя",
            "value": {
                "username": "ivan_petrov",
                "email": "ivan@example.com",
                "password": "strongpassword123",
            },
        },
        "weak_password": {
            "summary": "Слабый пароль",
            "description": "Пароль слишком короткий (если настроена валидация)",
            "value": {
                "username": "test_user",
                "email": "test@example.com",
                "password": "123",
            },
        },
        "duplicate": {
            "summary": "Пользователь уже существует",
            "description": "Попытка зарегистрировать существующего пользователя",
            "value": {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
            },
        },
    }
)


example_stats_params = {
    "fuel_consumption": {
        "summary": "Расход топлива",
        "description": "Параметры для расчёта среднего расхода топлива",
        "value": {"last_n": 5},
    },
    "cost_per_km": {
        "summary": "Стоимость километра",
        "description": "Период для расчёта стоимости километра",
        "value": {"start_date": "2024-01-01", "end_date": "2024-12-31"},
    },
    "compare": {
        "summary": "Сравнение автомобилей",
        "description": "ID двух автомобилей для сравнения",
        "value": {"car1": 1, "car2": 2},
    },
}
