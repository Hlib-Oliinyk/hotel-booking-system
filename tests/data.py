TEST_USER = {
    "email": "test@gmail.com",
    "password": "secret-password"
}

TEST_LOGIN = {
    "email": "test@gmail.com",
    "password": "secret-password"
}

TEST_ADMIN = {
    "email": "admin@gmail.com",
    "password": "admin-secret-password"
}

TEST_ADMIN_LOGIN = {
    "email": "admin@gmail.com",
    "password": "admin-secret-password"
}

TEST_HOTEL = {
    "title": "Test Hotel",
    "location": "Kyiv",
    "description": "A hotel for testing",
    "stars": 3
}

TEST_ROOM = {
    "number": "101",
    "room_type": "standard",
    "price_per_night": 1500,
    "description": "Cozy room"
}

TEST_BOOKING = {
    "check_in": (
            __import__("datetime").date.today()
            + __import__("datetime").timedelta(days=5)
    ).isoformat(),
    "check_out": (
            __import__("datetime").date.today()
            + __import__("datetime").timedelta(days=8)
    ).isoformat(),
}