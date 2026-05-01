from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  
    )
    
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    secret_key: str
    algo: str = "HS256"           
    access_token_expire_minutes: int = 30
    
    app_title: str = "Car Expense Analyzer API"
    app_version: str = "1.0.0"
    app_description: str = "REST-сервис для учёта расходов на автомобиль"
    
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:8000"
    ]
    
    default_reminder_step_km: int = 10000  # шаг для напоминаний о ТО (км)
    default_fuel_consumption_last_n: int = 5  # по умолчанию для расчёта расхода
    
    debug: bool = False
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def database_url_sqlite(self) -> str:
        return "sqlite:///./car_expenses.db"


settings = Settings()
