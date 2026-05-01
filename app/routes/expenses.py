from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.data_handler import (
    write_expense_to_csv,
    read_expenses_from_csv,
    delete_expense_from_csv
)

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/form", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense_form(
    car_id: int = Form(...),
    date: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    description: str = Form("")
):
    expense = ExpenseCreate(
        car_id=car_id,
        date=date,
        category=category,
        amount=amount,
        description=description
    )
    new_expense = write_expense_to_csv(expense)
    return new_expense

@router.get("/", response_model=List[ExpenseResponse])
def get_all_expenses(
    car_id: Optional[int] = Query(None, description="Фильтр по ID автомобиля")
):
    expenses = read_expenses_from_csv(car_id)
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found")
    return expenses


@router.delete("/{expense_id}")
def delete_expense(expense_id: int):
    if not delete_expense_from_csv(expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}
