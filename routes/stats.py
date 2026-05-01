from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
from app.analytics import (
    calculate_avg_fuel_consumption,
    calculate_cost_per_km,
    compare_cars
)
from app.data_handler import read_cars_from_csv

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/fuel_consumption/{car_id}")
def get_fuel_consumption(
    car_id: int,
    last_n: Optional[int] = Query(None, description="Количество последних заправок для расчёта")
):
    consumption = calculate_avg_fuel_consumption(car_id, last_n)
    if consumption is None:
        raise HTTPException(
            status_code=404,
            detail="Not enough fuelup data for this car (need at least 2 records)"
        )
    return {
        "car_id": car_id,
        "avg_fuel_consumption_L_per_100km": consumption,
        "based_on_last_n_fuelups": last_n or "all"
    }


@router.get("/cost_per_km/{car_id}")
def get_cost_per_km(
    car_id: int,
    start_date: Optional[date] = Query(None, description="Начало периода (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Конец периода (YYYY-MM-DD)")
):
    
    stats = calculate_cost_per_km(car_id, start_date, end_date)
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    return stats


@router.get("/compare")
def compare_two_cars(
    car1: int = Query(..., description="ID первого автомобиля"),
    car2: int = Query(..., description="ID второго автомобиля")
):
    cars = read_cars_from_csv()
    if not cars:
        raise HTTPException(status_code=404, detail="No cars found")
    
    car_ids = [int(c["id"]) for c in cars]
    if car1 not in car_ids or car2 not in car_ids:
        raise HTTPException(status_code=404, detail="One or both cars not found")
    
    comparison = compare_cars(car1, car2)
    return comparison
