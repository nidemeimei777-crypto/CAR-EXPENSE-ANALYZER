from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text
from app.db import get_async_session
from app.models import Car, Expense, FuelUp, Reminder
from app.schemas.schemas import CarCreate, CarResponse
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(
    car: CarCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Добавить новый автомобиль"""
    new_car = Car(
        brand=car.brand,
        model=car.model,
        year=car.year,
        license_plate=car.license_plate
    )
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
    return new_car


@router.get("/", response_model=List[CarResponse])
async def get_cars(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Получить список всех автомобилей"""
    result = await db.execute(select(Car))
    cars = result.scalars().all()
    return cars


@router.put("/{car_id}", response_model=CarResponse)
async def update_car(
    car_id: int,
    car_data: CarCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные автомобиля"""
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    car.brand = car_data.brand
    car.model = car_data.model
    car.year = car_data.year
    car.license_plate = car_data.license_plate
    
    await db.commit()
    await db.refresh(car)
    return car


@router.delete("/{car_id}")
async def delete_car(
    car_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удалить автомобиль и перенумеровать ID оставшихся"""
    # Проверяем существование автомобиля
    result = await db.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Удаляем связанные записи
    await db.execute(delete(Expense).where(Expense.car_id == car_id))
    await db.execute(delete(FuelUp).where(FuelUp.car_id == car_id))
    await db.execute(delete(Reminder).where(Reminder.car_id == car_id))
    
    # Удаляем автомобиль
    await db.delete(car)
    
    # Получаем все оставшиеся автомобили, отсортированные по ID
    result = await db.execute(select(Car).order_by(Car.id))
    remaining_cars = result.scalars().all()
    
    # Перенумеровываем ID начиная с 1
    counter = 1
    for old_car in remaining_cars:
        await db.execute(update(Car).where(Car.id == old_car.id).values(id=counter))
        counter += 1
    
    # Сбрасываем последовательность ID в PostgreSQL
    await db.execute(text("SELECT setval('cars_id_seq', (SELECT COALESCE(MAX(id), 1) FROM cars))"))
    
    await db.commit()
    return {"message": "Автомобиль успешно удален"}
