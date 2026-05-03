from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_async_session
from app.models import FuelUp, Car, Expense
from app.schemas.schemas import FuelUpCreate, FuelUpResponse, FuelUpWithExpenseCreate
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/fuelups", tags=["fuelups"])


@router.post("/", response_model=FuelUpResponse, status_code=status.HTTP_201_CREATED)
async def create_fuelup(
    fuelup: FuelUpCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Добавить заправку"""
    result = await db.execute(select(Car).where(Car.id == fuelup.car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    new_fuelup = FuelUp(
        car_id=fuelup.car_id,
        date=fuelup.date,
        liters=fuelup.liters,
        price_per_liter=fuelup.price_per_liter,
        odometer=fuelup.odometer,
    )
    db.add(new_fuelup)
    await db.commit()
    await db.refresh(new_fuelup)
    return new_fuelup


@router.post("/with_expense", status_code=status.HTTP_201_CREATED)
async def create_fuelup_with_expense(
    data: FuelUpWithExpenseCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Добавить заправку И автоматически создать расход"""
    try:
        # Проверяем существование автомобиля
        result = await db.execute(select(Car).where(Car.id == data.car_id))
        car = result.scalar_one_or_none()
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

        # 1. Создаём заправку
        new_fuelup = FuelUp(
            car_id=data.car_id,
            date=data.date,
            liters=data.liters,
            price_per_liter=data.price_per_liter,
            odometer=data.odometer,
        )
        db.add(new_fuelup)
        await db.flush() 

        print(f"✅ Заправка создана: id={new_fuelup.id}")

        # 2. Создаём расход
        amount = data.liters * data.price_per_liter
        new_expense = Expense(
            car_id=data.car_id,
            date=data.date,
            category="заправка",
            amount=amount,
            description=f"Заправка: {data.liters}л × {data.price_per_liter}₽/л",
        )
        db.add(new_expense)

        await db.commit()
        await db.refresh(new_fuelup)
        await db.refresh(new_expense)

        print(f"✅ Расход создан: id={new_expense.id}")

        return {
            "message": "Заправка и расход созданы",
            "fuelup": new_fuelup,
            "expense": new_expense,
        }

    except Exception as e:
        await db.rollback()
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[FuelUpResponse])
async def get_fuelups(
    car_id: Optional[int] = Query(None, description="Фильтр по ID автомобиля"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Получить все заправки (с фильтрацией)"""
    if car_id:
        result = await db.execute(select(FuelUp).where(FuelUp.car_id == car_id))
    else:
        result = await db.execute(select(FuelUp))
    fuelups = result.scalars().all()
    print(f"📊 Заправок в БД: {len(fuelups)}")
    return fuelups


@router.put("/{fuelup_id}", response_model=FuelUpResponse)
async def update_fuelup(
    fuelup_id: int,
    fuelup_data: FuelUpCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Обновить данные заправки"""
    result = await db.execute(select(FuelUp).where(FuelUp.id == fuelup_id))
    fuelup = result.scalar_one_or_none()
    if not fuelup:
        raise HTTPException(status_code=404, detail="Fuelup not found")

    fuelup.car_id = fuelup_data.car_id
    fuelup.date = fuelup_data.date
    fuelup.liters = fuelup_data.liters
    fuelup.price_per_liter = fuelup_data.price_per_liter
    fuelup.odometer = fuelup_data.odometer

    await db.commit()
    await db.refresh(fuelup)
    return fuelup


@router.delete("/{fuelup_id}")
async def delete_fuelup(
    fuelup_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Удалить заправку"""
    result = await db.execute(select(FuelUp).where(FuelUp.id == fuelup_id))
    fuelup = result.scalar_one_or_none()
    if not fuelup:
        raise HTTPException(status_code=404, detail="Fuelup not found")

    await db.delete(fuelup)
    await db.commit()
    return {"message": "Fuelup deleted successfully"}
