from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_async_session
from app.models import FuelUp
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/fuel_consumption/{car_id}")
async def get_fuel_consumption(
    car_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Рассчитать средний расход топлива (л/100км)"""
    result = await db.execute(
        select(FuelUp).where(FuelUp.car_id == car_id).order_by(FuelUp.date)
    )
    fuelups = result.scalars().all()

    if not fuelups or len(fuelups) < 2:
        return {
            "car_id": car_id,
            "avg_fuel_consumption_L_per_100km": None,
            "message": "Need at least 2 fuel-ups to calculate consumption",
        }

    total_liters = 0
    total_distance = 0

    for i in range(1, len(fuelups)):
        current = fuelups[i]
        previous = fuelups[i - 1]

        distance = current.odometer - previous.odometer
        if distance > 0:
            total_liters += current.liters
            total_distance += distance

    if total_distance > 0:
        avg_consumption = (total_liters / total_distance) * 100
        return {
            "car_id": car_id,
            "avg_fuel_consumption_L_per_100km": round(avg_consumption, 2),
            "total_liters": round(total_liters, 2),
            "total_distance_km": total_distance,
        }

    return {
        "car_id": car_id,
        "avg_fuel_consumption_L_per_100km": None,
        "message": "Not enough data to calculate consumption",
    }
