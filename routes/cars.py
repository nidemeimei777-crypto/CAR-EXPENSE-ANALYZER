from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.schemas import CarCreate, CarUpdate, CarResponse
from app.data_handler import (
    write_car_to_csv,
    read_cars_from_csv,
    read_car_from_csv,
    update_car_in_csv,
    delete_car_from_csv
)

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def create_car(car: CarCreate):
    new_car = write_car_to_csv(car)
    return new_car


@router.get("/", response_model=List[CarResponse])
def get_all_cars():
    cars = read_cars_from_csv()
    if not cars:
        raise HTTPException(status_code=404, detail="No cars found")
    return cars


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int):
    car = read_car_from_csv(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.put("/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car_update: CarUpdate):
    update_data = {k: v for k, v in car_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    updated = update_car_in_csv(car_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Car not found")
    return updated


@router.delete("/{car_id}")
def delete_car(car_id: int):
    if not delete_car_from_csv(car_id):
        raise HTTPException(status_code=404, detail="Car not found")
    return {"message": "Car deleted successfully"}
