from fastapi import APIRouter, Depends
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_async_session
from app.models import Expense, Car, FuelUp
from app.auth import get_current_user
from app.models import User
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from collections import defaultdict

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/expenses_by_category/{car_id}")
async def get_expenses_by_category(
    car_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Получить расходы по категориям для круговой диаграммы"""
    result = await db.execute(select(Expense).where(Expense.car_id == car_id))
    expenses = result.scalars().all()

    if not expenses:
        return {"categories": [], "amounts": [], "message": "Нет данных"}

    categories = defaultdict(float)
    category_names = {
        "заправка": "⛽ Заправка",
        "ремонт": "🔧 Ремонт",
        "мойка": "🧼 Мойка",
        "страховка": "📄 Страховка",
        "штраф": "⚠️ Штрафы",
        "транспортный налог": "🏛️ Транспортный налог",
        "платные дороги": "🛣️ Платные дороги",
        "другое": "📌 Другое",
    }

    for exp in expenses:
        cat = exp.category
        categories[cat] += exp.amount

    result_data = []
    for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        result_data.append(
            {"category": category_names.get(cat, cat), "amount": round(amount, 2)}
        )

    return {"categories": result_data, "total": sum(categories.values())}


@router.get("/pie_chart/{car_id}")
async def get_pie_chart(
    car_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """Сгенерировать круговую диаграмму расходов"""
    result = await db.execute(select(Expense).where(Expense.car_id == car_id))
    expenses = result.scalars().all()

    if not expenses:
        return {"image": None, "message": "Нет данных для построения диаграммы"}

    categories = defaultdict(float)
    category_names = {
        "заправка": "Заправка",
        "ремонт": "Ремонт",
        "мойка": "Мойка",
        "страховка": "Страховка",
        "штраф": "Штрафы",
        "транспортный налог": "Транспортный налог",
        "платные дороги": "Платные дороги",
        "другое": "Другое",
    }

    for exp in expenses:
        categories[exp.category] += exp.amount

    # Подготовка данных для графика
    labels = [category_names.get(cat, cat) for cat in categories.keys()]
    sizes = list(categories.values())
    colors = [
        "#667eea",
        "#48bb78",
        "#ed8936",
        "#e53e3e",
        "#38a169",
        "#dd6b20",
        "#4299e1",
        "#9f7aea",
    ]

    # Создание диаграммы
    plt.figure(figsize=(8, 6))
    plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors[: len(labels)],
        startangle=90,
    )
    plt.title(f"Расходы по категориям (Всего: {sum(sizes):.2f} ₽)", fontsize=14)
    plt.axis("equal")

    # Сохранение в base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return {"image": f"data:image/png;base64,{image_base64}"}


@router.get("/compare_cars")
async def compare_cars(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Сравнение автомобилей по расходам и эффективности"""
    # Получаем все автомобили
    cars_result = await db.execute(select(Car))
    cars = cars_result.scalars().all()

    if not cars:
        return []

    result = []
    for car in cars:
        # Получаем расходы
        expenses_result = await db.execute(
            select(Expense).where(Expense.car_id == car.id)
        )
        expenses = expenses_result.scalars().all()

        total_expenses = sum(e.amount for e in expenses)

        # Получаем заправки для расчёта расхода топлива
        fuelups_result = await db.execute(
            select(FuelUp).where(FuelUp.car_id == car.id).order_by(FuelUp.date)
        )
        fuelups = fuelups_result.scalars().all()

        avg_consumption = None
        if len(fuelups) >= 2:
            total_liters = 0
            total_distance = 0
            for i in range(1, len(fuelups)):
                distance = fuelups[i].odometer - fuelups[i - 1].odometer
                if distance > 0:
                    total_liters += fuelups[i].liters
                    total_distance += distance
            if total_distance > 0:
                avg_consumption = round((total_liters / total_distance) * 100, 2)

        # Эффективность = расходы на 100 км
        efficiency = None
        if avg_consumption:
            efficiency = (
                round((total_expenses / total_distance) * 100, 2)
                if total_distance > 0
                else None
            )

        result.append(
            {
                "id": car.id,
                "name": f"{car.brand} {car.model}",
                "license_plate": car.license_plate,
                "total_expenses": round(total_expenses, 2),
                "avg_fuel_consumption": avg_consumption,
                "efficiency_per_100km": efficiency,
                "expenses_count": len(expenses),
            }
        )

    # Сортируем по общим расходам
    result.sort(key=lambda x: x["total_expenses"], reverse=True)
    return result
