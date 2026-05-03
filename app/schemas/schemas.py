from datetime import date
from pydantic import BaseModel, field_validator
from typing import Optional


# ==================== АВТОМОБИЛИ ====================

class CarCreate(BaseModel):
    brand: str
    model: str
    year: int
    license_plate: str

    @field_validator('year')
    def validate_year(cls, v):
        if v < 1900 or v > 2026:
            raise ValueError('Год должен быть между 1900 и 2026')
        return v


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None


class CarResponse(CarCreate):
    id: int


# ==================== ЗАПРАВКИ ====================

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


#заправки и расходы

class FuelUpWithExpenseCreate(BaseModel):
    car_id: int
    date: date
    liters: float
    price_per_liter: float
    odometer: int


# ==================== РАСХОДЫ ====================

class ExpenseCreate(BaseModel):
    car_id: int
    date: date
    category: str
    amount: float
    description: Optional[str] = None

    @field_validator('category')
    def validate_category(cls, v):
        allowed = [
            'заправка', 'ремонт', 'мойка', 'штраф', 'платные дороги', 
            'страховка', 'транспортный налог',  'другое'
        ]
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


# ==================== ПРОБЕГ ====================

class OdometerReadingCreate(BaseModel):
    car_id: int
    date: date
    value: int
    description: Optional[str] = None


class OdometerReadingUpdate(BaseModel):
    date: Optional[date] = None
    value: Optional[int] = None
    description: Optional[str] = None


class OdometerReadingResponse(OdometerReadingCreate):
    id: int


# ==================== НАПОМИНАНИЯ ====================

class ReminderCreate(BaseModel):
    car_id: int
    due_date: date
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    triggered_at_odometer: Optional[int] = 0


class ReminderUpdate(BaseModel):
    due_date: Optional[date] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    triggered_at_odometer: Optional[int] = None


class ReminderResponse(ReminderCreate):
    id: int


# ==================== ПОЛЬЗОВАТЕЛИ ====================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
