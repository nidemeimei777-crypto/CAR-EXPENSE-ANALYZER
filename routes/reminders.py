from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from app.schemas import ReminderCreate, ReminderUpdate, ReminderResponse
from app.data_handler import (
    write_reminder_to_csv,
    read_reminders_from_csv,
    update_reminder_in_csv,
    delete_reminder_from_csv
)

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(reminder: ReminderCreate):
    new_reminder = write_reminder_to_csv(reminder)
    return new_reminder


@router.get("/", response_model=List[ReminderResponse])
def get_all_reminders(
    car_id: Optional[int] = Query(None, description="Фильтр по ID автомобиля"),
    only_active: bool = Query(False, description="Только активные (невыполненные)")
):
    reminders = read_reminders_from_csv(car_id, only_active)
    if not reminders:
        raise HTTPException(status_code=404, detail="No reminders found")
    return reminders


@router.patch("/{reminder_id}/complete", response_model=ReminderResponse)
def complete_reminder(reminder_id: int):
    updated = update_reminder_in_csv(reminder_id, {"is_completed": True})
    if not updated:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return updated


@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: int, reminder_update: ReminderUpdate):
    update_data = {k: v for k, v in reminder_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    updated = update_reminder_in_csv(reminder_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return updated


@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int):
    if not delete_reminder_from_csv(reminder_id):
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted successfully"}
