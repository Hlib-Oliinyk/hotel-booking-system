# Hotel Booking System

REST API для системи бронювання готелів на FastAPI з асинхронним доступом до PostgreSQL.

---

## Зміст

- [Функціонал](#функціонал)
- [Технологічний стек](#технологічний-стек)
- [Структура проєкту](#структура-проєкту)
- [Запуск локально](#запуск-локально)
- [API Endpoints](#api-endpoints)
- [Programming Principles](#programming-principles)
- [Design Patterns](#design-patterns)
- [Refactoring Techniques](#refactoring-techniques)

---

## Функціонал

### Автентифікація та авторизація
- Реєстрація та вхід користувачів
- JWT access-токени (зберігаються в `httponly` cookie)
- Refresh-токени (14 днів, ротація при кожному оновленні, хешуються SHA-256 перед збереженням)
- Два рівні доступу: `customer` та `admin`

### Управління готелями *(тільки admin)*
- Додавання, оновлення, видалення готелю
- Перегляд списку з фільтрацією за місцезнаходженням

### Управління кімнатами *(перегляд - всі, CRUD - тільки admin)*
- Додавання кімнати (тип, ціна за ніч, опис)
- Перегляд з фільтрацією за готелем, часткове оновлення (PATCH), видалення

### Бронювання
- Створення бронювання з автоматичним розрахунком вартості
- Перевірка доступності кімнати та конфліктів дат
- Перегляд власних бронювань та скасування

---

## Технологічний стек

| Компонент | Бібліотека |
|---|---|
| Веб-фреймворк | FastAPI 0.135.3 |
| ASGI-сервер | Uvicorn 0.44.0 |
| ORM | SQLAlchemy 2.0.49 (async) |
| Драйвер БД | asyncpg 0.31.0 |
| Міграції | Alembic 1.18.4 |
| Валідація | Pydantic 2.12.5 / pydantic-settings 2.13.1 |
| JWT | python-jose 3.5.0 |
| Хешування паролів | passlib + argon2-cffi |
| Тести | pytest 9.0.3 + pytest-asyncio 1.3.0 |
| Тестова БД | aiosqlite 0.22.1 |

---

## Структура проєкту

```
hotel-booking-system/
├── app/
│   ├── api/
│   │   ├── endpoints.py          # Підключення всіх роутерів
│   │   └── routes/
│   │       ├── auth.py           # Ендпоінти автентифікації
│   │       ├── booking.py        # Ендпоінти бронювання
│   │       ├── hotel.py          # Ендпоінти готелів
│   │       └── room.py           # Ендпоінти кімнат
│   ├── core/
│   │   └── config.py             # Налаштування (pydantic-settings)
│   ├── db/
│   │   ├── database.py           # Engine, сесії, Base модель
│   │   └── migrations/           # Alembic міграції
│   ├── models/                   # SQLAlchemy моделі
│   ├── repositories/             # Шар доступу до даних
│   │   ├── base.py               # BaseRepository з CRUD
│   │   ├── booking_repo.py
│   │   ├── hotel_repo.py
│   │   ├── room_repo.py
│   │   ├── token_repo.py
│   │   └── user_repo.py
│   ├── schemas/                  # Pydantic схеми (DTO)
│   ├── securities/
│   │   ├── authorization/jwt.py  # JWTGenerator
│   │   └── hashing.py            # Хешування паролів та токенів
│   ├── services/                 # Бізнес-логіка
│   ├── utils/exceptions/         # Кастомні виключення
│   ├── dependencies.py           # FastAPI Depends провайдери
│   ├── exceptions_handler.py     # Глобальна обробка винятків
│   └── main.py
├── tests/
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## Запуск локально

### 1. Клонування репозиторію

```bash
git clone https://github.com/Hlib-Oliinyk/hotel-booking-system
cd hotel_booking_system
```

### 2. Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 3. Налаштування змінних середовища

```bash
cp .env.example .env
```

```env
DB_NAME=hotel_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost

TEST_DB_URL=sqlite+aiosqlite:///./test.db

SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
```

### 4. Запуск PostgreSQL та створення бази

```bash
psql -U postgres -c "CREATE DATABASE hotel_db;"
```

### 5. Застосування міграцій

```bash
alembic upgrade head
```

### 6. Запуск сервера

```bash
uvicorn app.main:app --reload
```

Сервер: [http://localhost:8000](http://localhost:8000)
Swagger UI: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

### 7. Запуск тестів

```bash
pytest tests/ -v
```

---

## API Endpoints

### Auth - `/auth`

| Метод | Шлях | Опис | Доступ |
|---|---|---|---|
| `POST` | `/auth/register` | Реєстрація | Всі |
| `POST` | `/auth/login` | Вхід, отримання токенів | Всі |
| `POST` | `/auth/refresh` | Оновлення access-токена | Авторизовані |
| `DELETE` | `/auth/logout` | Вихід | Авторизовані |
| `GET` | `/auth/me` | Дані поточного користувача | Авторизовані |

### Hotels - `/hotel`

| Метод | Шлях | Опис | Доступ |
|---|---|---|---|
| `GET` | `/hotel` | Список (фільтр за `location`) | Всі |
| `POST` | `/hotel` | Створення | Admin |
| `PUT` | `/hotel/{hotel_id}` | Оновлення | Admin |
| `DELETE` | `/hotel/{hotel_id}` | Видалення | Admin |

### Rooms - `/rooms`

| Метод | Шлях | Опис | Доступ |
|---|---|---|---|
| `GET` | `/rooms` | Список (фільтр за `hotel_id`) | Всі |
| `GET` | `/rooms/{room_id}` | Кімната за ID | Всі |
| `POST` | `/rooms` | Створення | Admin |
| `PATCH` | `/rooms/{room_id}` | Часткове оновлення | Admin |
| `DELETE` | `/rooms/{room_id}` | Видалення | Admin |

### Bookings - `/booking`

| Метод | Шлях | Опис | Доступ |
|---|---|---|---|
| `POST` | `/booking` | Створення бронювання | Авторизовані |
| `GET` | `/booking/me` | Власні бронювання | Авторизовані |
| `PATCH` | `/booking/{booking_id}` | Скасування | Авторизовані |

---

## Programming Principles

### 1. Single Responsibility Principle (SRP)
Кожен клас відповідає за одну зону відповідальності. [`UserService`](app/services/user_service.py) - тільки бізнес-логіка користувачів, [`hashing.py`](app/securities/hashing.py) 
тільки хешування, [`jwt.py`](app/securities/authorization/jwt.py) - тільки робота з токенами.

### 2. Dependency Inversion Principle (DIP)
Сервіси залежать від репозиторіїв, переданих через конструктор. [`dependencies.py`](app/dependencies.py) виступає контейнером залежностей, який збирає весь граф об'єктів через FastAPI `Depends`.

### 3. DRY (Don't Repeat Yourself)
Спільні CRUD-операції реалізовані один раз у [`BaseRepository`](app/repositories/base.py). Усі конкретні репозиторії успадковують цю поведінку і лише розширюють її специфічними методами.

### 4. Fail Fast
Валідація відбувається якомога раніше: [`BookingCreate`](app/schemas/booking.py) перевіряє коректність дат ще до сервісного шару. Кастомні виключення з [`app/utils/exceptions/`](app/utils/exceptions/) кидаються одразу при виявленні проблеми.

### 5. Separation of Concerns
Чіткий поділ на шари: **Routes** -> **Services** -> **Repositories** -> **Models**. Роути в [`app/api/routes/`](app/api/routes/) не містять SQL-запитів, репозиторії не містять бізнес-правил.

### 6. Security by Design
Безпека закладена в архітектуру: паролі хешуються Argon2, refresh-токени зберігаються тільки у вигляді SHA-256 хешу, токени передаються через `httponly` cookie. Реалізація: [`hashing.py`](app/securities/hashing.py).

---

## Design Patterns

### 1. Repository Pattern

> **Навіщо:** ізолює бізнес-логіку від SQLAlchemy - сервіси не знають, як саме виконуються запити до БД. При тестуванні достатньо підмінити PostgreSQL на SQLite, не змінюючи жодного рядка в сервісах.

**Файли:** [`app/repositories/base.py`](app/repositories/base.py), [`booking_repo.py`](app/repositories/booking_repo.py), [`hotel_repo.py`](app/repositories/hotel_repo.py), [`room_repo.py`](app/repositories/room_repo.py), [`user_repo.py`](app/repositories/user_repo.py)

`BaseRepository` надає єдиний CRUD-інтерфейс, конкретні репозиторії успадковують його та додають специфічні запити:

```python
# app/repositories/base.py
class BaseRepository:
    model = None

    async def find_by_id(self, model_id: int):
        query = select(self.model).filter_by(id=model_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def add_one(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one()
```

```python
# app/repositories/hotel_repo.py
class HotelRepository(BaseRepository):
    model = Hotel

    async def get_filtered_hotels(self, location: str | None = None):
        query = select(self.model)
        if location:
            query = query.filter(self.model.location.icontains(location))
        result = await self.db.execute(query)
        return result.scalars().all()
```

---

### 2. Singleton

> **Навіщо:** `JWTGenerator` та `settings` мають існувати в єдиному екземплярі - повторне створення було б зайвим і могло б призводити до неузгодженості конфігурації по всьому застосунку.

**Файли:** [`app/securities/authorization/jwt.py`](app/securities/authorization/jwt.py), [`app/core/config.py`](app/core/config.py)

```python
# app/securities/authorization/jwt.py
class JWTGenerator:
    def generate_access_token(self, user: User) -> str:
        return self._generate_jwt_token(data={"sub": str(user.id)})

    def get_details_from_token(self, token: str) -> int:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return int(payload.get("sub"))

# Єдиний глобальний екземпляр для всього застосунку
jwt_generator: JWTGenerator = get_jwt_token()
```

```python
# app/core/config.py
class Settings(BaseSettings):
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ...

# Єдиний глобальний екземпляр конфігурації
settings = Settings()
```

---

### 3. Template Method

> **Навіщо:** `BaseRepository` визначає скелет алгоритму роботи з БД (select -> execute -> return), а підкласи уточнюють або розширюють окремі кроки під свої потреби, не переписуючи загальну логіку.

**Файли:** [`app/repositories/base.py`](app/repositories/base.py) та всі дочірні репозиторії

```python
# Базовий "скелет" у BaseRepository
async def find_all(self, **filter_by):
    query = select(self.model).filter_by(**filter_by)
    result = await self.db.execute(query)
    return result.scalars().all()

# BookingRepository розширює базовий підхід власним складним запитом
# app/repositories/booking_repo.py
async def get_booked_count(self, room_id: int, check_in, check_out):
    query = (
        select(func.count(Booking.id))
        .where(
            Booking.room_id == room_id,
            Booking.check_in < check_out,
            Booking.check_out > check_in,
            Booking.status != "cancelled"
        )
    )
    result = await self.db.execute(query)
    return result.scalar() or 0
```

---

### 4. Facade

> **Навіщо:** роути повинні залишатись простими - тільки HTTP-логіка. [`dependencies.py`](app/dependencies.py) приховує за простими функціями всю складність: відкриття сесії БД, створення репозиторіїв, збирання сервісів та перевірку авторизації.

**Файл:** [`app/dependencies.py`](app/dependencies.py)

```python
# Роут отримує готовий сервіс - без жодних деталей його створення
# app/api/routes/booking.py
@router.post("")
async def add_booking(
    booking_data: BookingCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    booking_service: Annotated[BookingService, Depends(get_booking_service)]
): ...

# app/dependencies.py
async def get_booking_service(db: Annotated[AsyncSession, Depends(get_db)]) -> BookingService:
    return BookingService(BookingRepository(db), RoomRepository(db))

async def get_current_user(
    token: Annotated[str, Depends(get_token_from_header_or_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    user_id = jwt_generator.get_details_from_token(token)
    return await user_service.get_user(user_id)
```

---

## Refactoring Techniques

### 1. Extract Class
Кожна сутність отримала окремий клас-репозиторій ([`UserRepository`](app/repositories/user_repo.py), [`HotelRepository`](app/repositories/hotel_repo.py), [`BookingRepository`](app/repositories/booking_repo.py) тощо). Базова CRUD-логіка винесена в [`BaseRepository`](app/repositories/base.py).

### 2. Extract Method
У [`JWTGenerator`](app/securities/authorization/jwt.py) приватний метод `_generate_jwt_token` інкапсулює логіку кодування JWT. Публічні методи `generate_access_token` та `get_details_from_token` делегують йому роботу, не дублюючи код.

### 3. Replace Magic Strings with Enum
У [`app/models/user.py`](app/models/user.py) ролі замінено на `UserRole(str, enum.Enum)` з `ADMIN` та `CUSTOMER`, що усуває "магічні рядки" типу `"admin"` та захищає від друкарських помилок.

### 4. Introduce Parameter Object
Замість передачі окремих параметрів введено Pydantic-схеми [`UserCreate`](app/schemas/user.py), [`BookingCreate`](app/schemas/booking.py), [`RoomCreate`](app/schemas/room.py) тощо. Вони групують дані та додають автоматичну валідацію.

### 5. Replace Conditional with Custom Exception
Замість `if ... return JSONResponse(...)` у сервісах - ієрархія кастомних виключень [`AppError`](app/utils/exceptions/base.py) -> [`BookingNotFound`](app/utils/exceptions/booking.py), [`RoomAlreadyBooked`](app/utils/exceptions/room.py) тощо. Централізована обробка в [`exceptions_handler.py`](app/exceptions_handler.py).

### 6. Decompose Conditional
У [`dependencies.py`](app/dependencies.py) функція `get_token_from_header_or_cookie` виокремлює логіку отримання токена (з заголовка `Authorization` або cookie) в один Depends-провайдер замість дублювання у кожному захищеному роуті.

### 7. Move Method to Appropriate Layer
Бізнес-логіка переміщена до сервісного шару. Перевірка конфліктів дат, розрахунок `total_cost` та перевірка статусу кімнати знаходяться у [`BookingService`](app/services/booking_service.py), а не у роуті чи репозиторії.