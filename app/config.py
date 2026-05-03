from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # JWT настройки (из .env)
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algo: str = "HS256"
    access_token_expire_minutes: int = 30

    # Настройки приложения
    app_title: str = "Car Expense Analyzer API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Дополнительные параметры
    default_reminder_step_km: int = 10000
    default_fuel_consumption_last_n: int = 5

    # Настройки базы данных
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "car_expenses"

    class Config:
        env_file = ".env"


settings = Settings()
