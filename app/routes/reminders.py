from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_async_session
from app.models import Reminder, Car
from app.schemas.schemas import ReminderCreate, ReminderResponse
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder: ReminderCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Создать напоминание"""
    result = await db.execute(select(Car).where(Car.id == reminder.car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    new_reminder = Reminder(
        car_id=reminder.car_id,
        due_date=reminder.due_date,
        title=reminder.title,
        description=reminder.description,
        is_completed=reminder.is_completed,
        triggered_at_odometer=reminder.triggered_at_odometer
    )
    db.add(new_reminder)
    await db.commit()
    await db.refresh(new_reminder)
    return new_reminder


@router.get("/", response_model=List[ReminderResponse])
async def get_reminders(
    car_id: Optional[int] = Query(None, description="Фильтр по ID автомобиля"),
    active_only: bool = Query(False, description="Только активные"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Получить все напоминания (с фильтрацией)"""
    if car_id:
        result = await db.execute(select(Reminder).where(Reminder.car_id == car_id))
    else:
        result = await db.execute(select(Reminder))
    reminders = result.scalars().all()
    
    if active_only:
        reminders = [r for r in reminders if not r.is_completed]
    return reminders


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    reminder_data: ReminderCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные напоминания"""
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    car_result = await db.execute(select(Car).where(Car.id == reminder_data.car_id))
    if not car_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Car not found")
    
    reminder.car_id = reminder_data.car_id
    reminder.due_date = reminder_data.due_date
    reminder.title = reminder_data.title
    reminder.description = reminder_data.description
    reminder.is_completed = reminder_data.is_completed
    reminder.triggered_at_odometer = reminder_data.triggered_at_odometer
    
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.patch("/{reminder_id}")
async def complete_reminder(
    reminder_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Отметить напоминание как выполненное"""
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.is_completed = True
    await db.commit()
    return {"message": "Reminder completed"}


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удалить напоминание"""
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    await db.delete(reminder)
    await db.commit()
    return {"message": "Reminder deleted successfully"}
