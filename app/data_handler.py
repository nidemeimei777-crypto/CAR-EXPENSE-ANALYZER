import csv
from typing import List, Optional, Dict, Any, Tuple
from app.schemas import CarCreate, FuelUpCreate, ExpenseCreate, ReminderCreate


# ==================== Вспомогательные функции ====================

def _get_next_id(csv_file_path: str) -> int:
    """Возвращает следующий доступный ID для новой записи"""
    try:
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            ids = [int(row.get('id', 0)) for row in reader if row.get('id')]
            return max(ids) + 1 if ids else 1
    except FileNotFoundError:
        return 1


def _write_to_csv(csv_file_path: str, data: Dict[str, Any], fieldnames: List[str]) -> Dict[str, Any]:
    """Универсальная запись в CSV-файл"""
    with open(csv_file_path, 'a+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(data)
    return data


# ==================== Работа с автомобилями ====================

CARS_CSV = "cars.csv"
CARS_FIELDNAMES = ["id", "brand", "model", "year", "license_plate"]


def write_car_to_csv(car: CarCreate) -> Dict[str, Any]:
    """Создаёт новую запись об автомобиле в CSV"""
    car_id = _get_next_id(CARS_CSV)
    car_data = car.dict()
    car_data["id"] = car_id
    return _write_to_csv(CARS_CSV, car_data, CARS_FIELDNAMES)


def read_cars_from_csv() -> Optional[List[Dict[str, Any]]]:
    """Возвращает список всех автомобилей"""
    try:
        with open(CARS_CSV, 'r') as csvfile:
            return list(csv.DictReader(csvfile))
    except FileNotFoundError:
        return None


def read_car_from_csv(car_id: int, return_line_num: bool = False) -> Optional[Tuple[int, Dict] | Dict]:
    """Возвращает автомобиль по ID"""
    try:
        with open(CARS_CSV, 'r') as csvfile:
            rows = csv.reader(csvfile)
            try:
                headers = next(rows)
            except StopIteration:
                return None
            for line_num, row in enumerate(rows, start=2):
                if row[0] == str(car_id):
                    car = dict(zip(headers, row))
                    return (line_num, car) if return_line_num else car
            return None
    except FileNotFoundError:
        return None


def update_car_in_csv(car_id: int, data_for_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обновляет данные автомобиля"""
    found = read_car_from_csv(car_id, return_line_num=True)
    if not found:
        return None
    
    line_num, car = found
    car.update(data_for_update)
    
    with open(CARS_CSV, 'r') as read_file:
        rows = list(csv.reader(read_file))
        rows[line_num - 1] = [car.get(field, "") for field in CARS_FIELDNAMES]
    
    with open(CARS_CSV, 'w', newline='') as write_file:
        writer = csv.writer(write_file)
        writer.writerows(rows)
    
    return car


def delete_car_from_csv(car_id: int) -> bool:
    """Удаляет автомобиль и все связанные с ним записи"""
    car_found = read_car_from_csv(car_id)
    if not car_found:
        return False
    
    # Удаляем автомобиль
    with open(CARS_CSV, 'r') as read_file:
        rows = list(csv.reader(read_file))
        new_rows = [row for row in rows if row[0] != str(car_id)]
    
    with open(CARS_CSV, 'w', newline='') as write_file:
        writer = csv.writer(write_file)
        writer.writerows(new_rows)
    
    # Удаляем все связанные заправки, расходы, напоминания
    delete_fuelups_by_car(car_id)
    delete_expenses_by_car(car_id)
    delete_reminders_by_car(car_id)
    
    return True


# ==================== Работа с заправками ====================

FUELUPS_CSV = "fuelups.csv"
FUELUPS_FIELDNAMES = ["id", "car_id", "date", "liters", "price_per_liter", "odometer"]


def write_fuelup_to_csv(fuelup: FuelUpCreate) -> Dict[str, Any]:
    """Создаёт новую запись о заправке"""
    fuelup_id = _get_next_id(FUELUPS_CSV)
    fuelup_data = fuelup.dict()
    fuelup_data["id"] = fuelup_id
    return _write_to_csv(FUELUPS_CSV, fuelup_data, FUELUPS_FIELDNAMES)


def read_fuelups_from_csv(car_id: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
    """Возвращает все заправки (или только для конкретного автомобиля)"""
    try:
        with open(FUELUPS_CSV, 'r') as csvfile:
            fuelups = list(csv.DictReader(csvfile))
            if car_id is not None:
                fuelups = [f for f in fuelups if int(f.get("car_id", 0)) == car_id]
            return fuelups if fuelups else None
    except FileNotFoundError:
        return None


def read_fuelup_from_csv(fuelup_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает заправку по ID"""
    try:
        with open(FUELUPS_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row.get("id", 0)) == fuelup_id:
                    return row
            return None
    except FileNotFoundError:
        return None


def update_fuelup_in_csv(fuelup_id: int, data_for_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обновляет запись о заправке"""
    try:
        with open(FUELUPS_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            headers = rows[0]
            
            for i, row in enumerate(rows[1:], start=1):
                if row[0] == str(fuelup_id):
                    fuelup = dict(zip(headers, row))
                    fuelup.update({k: str(v) for k, v in data_for_update.items()})
                    rows[i] = [fuelup.get(h, "") for h in headers]
                    
                    with open(FUELUPS_CSV, 'w', newline='') as write_file:
                        writer = csv.writer(write_file)
                        writer.writerows(rows)
                    return fuelup
            return None
    except FileNotFoundError:
        return None


def delete_fuelup_from_csv(fuelup_id: int) -> bool:
    """Удаляет запись о заправке"""
    try:
        with open(FUELUPS_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            new_rows = [row for row in rows if row[0] != str(fuelup_id)]
        
        with open(FUELUPS_CSV, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(new_rows)
        return True
    except FileNotFoundError:
        return False


def delete_fuelups_by_car(car_id: int) -> None:
    """Удаляет все заправки, связанные с автомобилем"""
    try:
        with open(FUELUPS_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            new_rows = [rows[0]] + [row for row in rows[1:] if row[1] != str(car_id)]
        
        with open(FUELUPS_CSV, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(new_rows)
    except FileNotFoundError:
        pass


# ==================== Работа с расходами ====================

EXPENSES_CSV = "expenses.csv"
EXPENSES_FIELDNAMES = ["id", "car_id", "date", "category", "amount", "description"]


def write_expense_to_csv(expense: ExpenseCreate) -> Dict[str, Any]:
    """Создаёт новую запись о расходе"""
    expense_id = _get_next_id(EXPENSES_CSV)
    expense_data = expense.dict()
    expense_data["id"] = expense_id
    return _write_to_csv(EXPENSES_CSV, expense_data, EXPENSES_FIELDNAMES)


def read_expenses_from_csv(car_id: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
    """Возвращает все расходы (или только для конкретного автомобиля)"""
    try:
        with open(EXPENSES_CSV, 'r') as csvfile:
            expenses = list(csv.DictReader(csvfile))
            if car_id is not None:
                expenses = [e for e in expenses if int(e.get("car_id", 0)) == car_id]
            return expenses if expenses else None
    except FileNotFoundError:
        return None


def delete_expense_from_csv(expense_id: int) -> bool:
    """Удаляет запись о расходе"""
    try:
        with open(EXPENSES_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            new_rows = [row for row in rows if row[0] != str(expense_id)]
        
        with open(EXPENSES_CSV, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(new_rows)
        return True
    except FileNotFoundError:
        return False


def delete_expenses_by_car(car_id: int) -> None:
    """Удаляет все расходы, связанные с автомобилем"""
    try:
        with open(EXPENSES_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            new_rows = [rows[0]] + [row for row in rows[1:] if row[1] != str(car_id)]
        
        with open(EXPENSES_CSV, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(new_rows)
    except FileNotFoundError:
        pass


# ==================== Работа с напоминаниями ====================

REMINDERS_CSV = "reminders.csv"
REMINDERS_FIELDNAMES = ["id", "car_id", "due_date", "title", "description", "is_completed", "triggered_at_odometer"]


def write_reminder_to_csv(reminder: ReminderCreate) -> Dict[str, Any]:
    """Создаёт новое напоминание"""
    reminder_id = _get_next_id(REMINDERS_CSV)
    reminder_data = reminder.dict()
    reminder_data["id"] = reminder_id
    return _write_to_csv(REMINDERS_CSV, reminder_data, REMINDERS_FIELDNAMES)


def read_reminders_from_csv(car_id: Optional[int] = None, only_active: bool = False) -> Optional[List[Dict[str, Any]]]:
    """Возвращает напоминания (фильтрация по автомобилю и статусу)"""
    try:
        with open(REMINDERS_CSV, 'r') as csvfile:
            reminders = list(csv.DictReader(csvfile))
            if car_id is not None:
                reminders = [r for r in reminders if int(r.get("car_id", 0)) == car_id]
            if only_active:
                reminders = [r for r in reminders if r.get("is_completed", "False") != "True"]
            return reminders if reminders else None
    except FileNotFoundError:
        return None


def update_reminder_in_csv(reminder_id: int, data_for_update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Обновляет напоминание (например, отметить выполненным)"""
    try:
        with open(REMINDERS_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            headers = rows[0]
            
            for i, row in enumerate(rows[1:], start=1):
                if row[0] == str(reminder_id):
                    reminder = dict(zip(headers, row))
                    reminder.update({k: str(v) for k, v in data_for_update.items()})
                    rows[i] = [reminder.get(h, "") for h in headers]
                    
                    with open(REMINDERS_CSV, 'w', newline='') as write_file:
                        writer = csv.writer(write_file)
                        writer.writerows(rows)
                    return reminder
            return None
    except FileNotFoundError:
        return None


def delete_reminder_from_csv(reminder_id: int) -> bool:
    """Удаляет напоминание"""
    try:
        with open(REMINDERS_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            new_rows = [row for row in rows if row[0] != str(reminder_id)]
        
        with open(REMINDERS_CSV, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(new_rows)
        return True
    except FileNotFoundError:
        return False


def delete_reminders_by_car(car_id: int) -> None:
    """Удаляет все напоминания, связанные с автомобилем"""
    try:
        with open(REMINDERS_CSV, 'r') as read_file:
            rows = list(csv.reader(read_file))
            new_rows = [rows[0]] + [row for row in rows[1:] if row[1] != str(car_id)]
        
        with open(REMINDERS_CSV, 'w', newline='') as write_file:
            writer = csv.writer(write_file)
            writer.writerows(new_rows)
    except FileNotFoundError:
        pass

# ==================== Работа с пользователями (для аутентификации) ====================

USERS_CSV = "users.csv"
USERS_FIELDNAMES = ["id", "username", "email", "hashed_password", "is_active", "created_at"]


def write_user_to_csv(user_data: dict) -> dict:
    """Создаёт нового пользователя в CSV"""
    user_id = _get_next_id(USERS_CSV)
    user_data["id"] = user_id
    if "created_at" not in user_data:
        user_data["created_at"] = datetime.now().isoformat()
    if "is_active" not in user_data:
        user_data["is_active"] = True
    return _write_to_csv(USERS_CSV, user_data, USERS_FIELDNAMES)


def read_user_from_csv(username: str) -> Optional[dict]:
    """Возвращает пользователя по имени пользователя"""
    try:
        with open(USERS_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("username") == username:
                    return row
            return None
    except FileNotFoundError:
        return None


def read_user_by_email_from_csv(email: str) -> Optional[dict]:
    """Возвращает пользователя по email"""
    try:
        with open(USERS_CSV, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("email") == email:
                    return row
            return None
    except FileNotFoundError:
        return None


def user_exists(username: str, email: str) -> bool:
    """Проверяет, существует ли пользователь с таким username или email"""
    return read_user_from_csv(username) is not None or read_user_by_email_from_csv(email) is not None
