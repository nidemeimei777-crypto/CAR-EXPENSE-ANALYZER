from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_async_session
from app.models import Expense, Car
from app.schemas.schemas import ExpenseCreate, ExpenseResponse
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Добавить расход"""
    result = await db.execute(select(Car).where(Car.id == expense.car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    
    new_expense = Expense(
        car_id=expense.car_id,
        date=expense.date,
        category=expense.category,
        amount=expense.amount,
        description=expense.description
    )
    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)
    return new_expense


@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    car_id: Optional[int] = Query(None, description="Фильтр по ID автомобиля"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Получить все расходы (с фильтрацией)"""
    if car_id:
        result = await db.execute(select(Expense).where(Expense.car_id == car_id))
    else:
        result = await db.execute(select(Expense))
    expenses = result.scalars().all()
    return expenses


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные расхода"""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Проверяем существование автомобиля
    car_result = await db.execute(select(Car).where(Car.id == expense_data.car_id))
    if not car_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Car not found")
    
    expense.car_id = expense_data.car_id
    expense.date = expense_data.date
    expense.category = expense_data.category
    expense.amount = expense_data.amount
    expense.description = expense_data.description
    
    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удалить расход"""
    result = await db.execute(select(Expense).where(Expense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    await db.delete(expense)
    await db.commit()
    return {"message": "Expense deleted successfully"}
