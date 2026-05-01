from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routes import cars, fuelups, expenses, reminders, stats, auth

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="Car Expense Analyzer")

app.include_router(cars.router)
app.include_router(fuelups.router)
app.include_router(expenses.router)
app.include_router(reminders.router)
app.include_router(stats.router)
app.include_router(auth.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
