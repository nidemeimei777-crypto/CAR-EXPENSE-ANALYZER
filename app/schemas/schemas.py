from pydantic import BaseModel
from datetime import date
from typing import Optional

class CarCreate(BaseModel):
    brand: str
    model: str
    year: int
    license_plate: str

class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None

class CarResponse(CarCreate):
    id: int

class FuelUpCreate(BaseModel):
    car_id: int
    date: date
    liters: float
    price_per_liter: float
    odometer: int

class FuelUpUpdate(BaseModel):
    date: Optional[date] = None
    liters: Optional[float] = None
    price_per_liter: Optional[float] = None
    odometer: Optional[int] = None

class FuelUpResponse(FuelUpCreate):
    id: int

class ExpenseCreate(BaseModel):
    car_id: int
    date: date
    category: str  # fuel, repair, insurance, wash, other
    amount: float
    description: Optional[str] = None

    @field_validator('category')
    def validate_category(cls, v):
        allowed = ['бензин', 'газ', 'ремонт', 'мойка', 'страховка', 'другое']
        if v not in allowed:
            raise ValueError(f'Категория должна быть одной из: {allowed}')
        return v

class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None

class ExpenseResponse(ExpenseCreate):
    id: int

class ReminderCreate(BaseModel):
    car_id: int
    due_date: date
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    triggered_at_odometer: Optional[int] = None

class ReminderUpdate(BaseModel):
    due_date: Optional[date] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    triggered_at_odometer: Optional[int] = None

class ReminderResponse(ReminderCreate):
    id: int

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
