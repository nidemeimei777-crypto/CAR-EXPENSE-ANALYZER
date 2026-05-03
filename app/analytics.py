from datetime import date
from typing import Optional
from app.data_handler import read_fuelups_from_csv, read_expenses_from_csv


def calculate_avg_fuel_consumption(car_id: int, last_n: Optional[int] = None) -> Optional[float]:
    fuelups = read_fuelups_from_csv(car_id)
    if not fuelups or len(fuelups) < 2:
        return None
    
    fuelups = sorted(fuelups, key=lambda x: int(x["odometer"]))
    
    if last_n:
        fuelups = fuelups[-last_n:]
    
    total_liters = 0.0
    total_distance = 0
    
    for i in range(1, len(fuelups)):
        dist = int(fuelups[i]["odometer"]) - int(fuelups[i-1]["odometer"])
        if dist > 0:
            total_liters += float(fuelups[i]["liters"])
            total_distance += dist
    
    if total_distance == 0:
        return None
    
    return round((total_liters / total_distance) * 100, 2)


def calculate_cost_per_km(car_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
    fuelups = read_fuelups_from_csv(car_id)
    expenses = read_expenses_from_csv(car_id)
    
    if not fuelups or len(fuelups) < 2:
        return {"error": "Not enough fuelup data"}
    if start_date:
        fuelups = [f for f in fuelups if date.fromisoformat(f["date"]) >= start_date]
        expenses = [e for e in expenses if date.fromisoformat(e["date"]) >= start_date] if expenses else []
    if end_date:
        fuelups = [f for f in fuelups if date.fromisoformat(f["date"]) <= end_date]
        expenses = [e for e in expenses if date.fromisoformat(e["date"]) <= end_date] if expenses else []
    
    if len(fuelups) < 2:
        return {"error": "Not enough fuelup data for period"}
    
    total_fuel_cost = sum(float(f["liters"]) * float(f["price_per_liter"]) for f in fuelups)
    total_expenses = sum(float(e["amount"]) for e in expenses) if expenses else 0
    
    total_cost = total_fuel_cost + total_expenses
    
    start_odometer = int(fuelups[0]["odometer"])
    end_odometer = int(fuelups[-1]["odometer"])
    total_distance = end_odometer - start_odometer
    
    if total_distance <= 0:
        return {"error": "Invalid odometer readings"}
    
    return {
        "car_id": car_id,
        "total_distance_km": total_distance,
        "total_cost": round(total_cost, 2),
        "fuel_cost": round(total_fuel_cost, 2),
        "expenses_cost": round(total_expenses, 2),
        "cost_per_km": round(total_cost / total_distance, 2),
    }


def compare_cars(car_id_1: int, car_id_2: int) -> dict:
    stats_1 = calculate_cost_per_km(car_id_1)
    stats_2 = calculate_cost_per_km(car_id_2)
    
    consumption_1 = calculate_avg_fuel_consumption(car_id_1)
    consumption_2 = calculate_avg_fuel_consumption(car_id_2)
    
    return {
        "car_1": {
            "avg_fuel_consumption_L_per_100km": consumption_1,
            "cost_per_km_rub": stats_1.get("cost_per_km") if "error" not in stats_1 else None,
        },
        "car_2": {
            "avg_fuel_consumption_L_per_100km": consumption_2,
            "cost_per_km_rub": stats_2.get("cost_per_km") if "error" not in stats_2 else None,
        },
        "verdict": "Car 1 is cheaper" if stats_1.get("cost_per_km", float('inf')) < stats_2.get("cost_per_km", float('inf')) else "Car 2 is cheaper"
    }
