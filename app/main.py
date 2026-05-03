from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.db import async_engine, Base
from app.routes import cars, fuelups, expenses, reminders, stats, auth, analytics


# Создание таблиц при запуске
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


templates = Jinja2Templates(directory="templates")

app = FastAPI(title="Car Expense Analyzer", lifespan=lifespan)

app.include_router(cars.router)
app.include_router(fuelups.router)
app.include_router(expenses.router)
app.include_router(reminders.router)
app.include_router(stats.router)
app.include_router(auth.router)
app.include_router(analytics.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
