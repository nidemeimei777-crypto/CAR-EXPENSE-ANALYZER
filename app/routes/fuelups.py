from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.schemas import FuelUpCreate, FuelUpUpdate, FuelUpResponse
from app.data_handler import (
    write_fuelup_to_csv,
    read_fuelups_from_csv,
    read_fuelup_from_csv,
    update_fuelup_in_csv,
    delete_fuelup_from_csv
)

router = APIRouter(prefix="/fuelups", tags=["fuelups"])


@router.post("/", response_model=FuelUpResponse, status_code=status.HTTP_201_CREATED)
def create_fuelup(fuelup: FuelUpCreate):
    new_fuelup = write_fuelup_to_csv(fuelup)
    return new_fuelup


@router.get("/", response_model=List[FuelUpResponse])
def get_all_fuelups(
    car_id: Optional[int] = Query(None, description="Фильтр по ID автомобиля")
):
    fuelups = read_fuelups_from_csv(car_id)
    if not fuelups:
        raise HTTPException(status_code=404, detail="No fuelups found")
    return fuelups


@router.get("/{fuelup_id}", response_model=FuelUpResponse)
def get_fuelup(fuelup_id: int):
    fuelup = read_fuelup_from_csv(fuelup_id)
    if not fuelup:
        raise HTTPException(status_code=404, detail="Fuelup not found")
    return fuelup


@router.put("/{fuelup_id}", response_model=FuelUpResponse)
def update_fuelup(fuelup_id: int, fuelup_update: FuelUpUpdate):
    update_data = {k: v for k, v in fuelup_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    updated = update_fuelup_in_csv(fuelup_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Fuelup not found")
    return updated


@router.delete("/{fuelup_id}")
def delete_fuelup(fuelup_id: int):
    if not delete_fuelup_from_csv(fuelup_id):
        raise HTTPException(status_code=404, detail="Fuelup not found")
    return {"message": "Fuelup deleted successfully"}
