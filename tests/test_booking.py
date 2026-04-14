import pytest
from datetime import date, timedelta

from tests.data import TEST_ROOM, TEST_BOOKING


def future_date(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


class TestCreateBooking:

    @pytest.mark.asyncio
    async def test_create_booking_success(self, authorized_client, get_hotel_id, room_number):
        response = await authorized_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["total_cost"] > 0
        assert "id" in data
        assert "user_id" in data
        assert "room_id" in data

    @pytest.mark.asyncio
    async def test_create_booking_unauthorized(self, async_client, get_hotel_id, room_number):
        response = await async_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_booking_nonexistent_hotel(self, authorized_client, room_number):
        response = await authorized_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": 999999,
            "room_number": room_number,
        })
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_booking_nonexistent_room(self, authorized_client, get_hotel_id):
        response = await authorized_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": "NON_EXISTENT_999",
        })
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_booking_past_check_in(self, authorized_client, get_hotel_id, room_number):
        response = await authorized_client.post("/booking", json={
            "hotel_id": get_hotel_id,
            "room_number": room_number,
            "check_in": (date.today() - timedelta(days=1)).isoformat(),
            "check_out": future_date(3),
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_check_out_before_check_in(self, authorized_client, get_hotel_id, room_number):
        response = await authorized_client.post("/booking", json={
            "hotel_id": get_hotel_id,
            "room_number": room_number,
            "check_in": future_date(5),
            "check_out": future_date(2),
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_same_dates(self, authorized_client, get_hotel_id, room_number):
        same_day = future_date(3)
        response = await authorized_client.post("/booking", json={
            "hotel_id": get_hotel_id,
            "room_number": room_number,
            "check_in": same_day,
            "check_out": same_day,
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_duplicate_raises_conflict(
        self,
        authorized_client,
        get_hotel_id,
        room_number
    ):
        payload = {
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        }
        first = await authorized_client.post("/booking", json=payload)
        assert first.status_code == 200

        second = await authorized_client.post("/booking", json=payload)
        assert second.status_code == 409

    @pytest.mark.asyncio
    async def test_create_booking_missing_fields(self, authorized_client):
        response = await authorized_client.post("/booking", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_booking_total_cost_calculated_correctly(self, authorized_client, get_hotel_id, room_number):
        check_in = future_date(10)
        check_out = future_date(13)
        response = await authorized_client.post("/booking", json={
            "hotel_id": get_hotel_id,
            "room_number": room_number,
            "check_in": check_in,
            "check_out": check_out,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_cost"] == TEST_ROOM["price_per_night"] * 3


class TestGetMyBookings:

    @pytest.mark.asyncio
    async def test_get_my_bookings_empty(self, authorized_client):
        response = await authorized_client.get("/booking/me")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_my_bookings_returns_own_booking(
        self,
        authorized_client,
        get_hotel_id,
        room_number
    ):
        await authorized_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })
        response = await authorized_client.get("/booking/me")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all("id" in b and "status" in b for b in data)

    @pytest.mark.asyncio
    async def test_get_my_bookings_unauthorized(self, async_client):
        response = await async_client.get("/booking/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_my_bookings_does_not_return_other_users_bookings(
        self,
        authorized_client,
        admin_client,
        get_hotel_id,
        room_number
    ):
        await admin_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })

        response = await authorized_client.get("/booking/me")
        assert response.status_code == 200
        for booking in response.json():
            assert booking["user_id"] != (await admin_client.get("/auth/me")).json()["id"]


class TestCancelBooking:

    @pytest.mark.asyncio
    async def test_cancel_booking_success(self, authorized_client, get_hotel_id, room_number):
        create = await authorized_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })
        booking_id = create.json()["id"]

        response = await authorized_client.patch(f"/booking/{booking_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_booking_unauthorized(
        self,
        async_client,
        authorized_client,
        get_hotel_id,
        room_number
    ):
        create = await authorized_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })
        booking_id = create.json()["id"]

        response = await async_client.patch(f"/booking/{booking_id}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cancel_booking_nonexistent(self, authorized_client):
        response = await authorized_client.patch("/booking/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_booking_twice_raises_error(self, authorized_client, get_hotel_id, room_number):
        create = await authorized_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })
        booking_id = create.json()["id"]

        await authorized_client.patch(f"/booking/{booking_id}")
        response = await authorized_client.patch(f"/booking/{booking_id}")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_cancel_someone_elses_booking(
        self,
        authorized_client,
        admin_client,
        get_hotel_id, room_number
    ):
        create = await admin_client.post("/booking", json={
            **TEST_BOOKING,
            "hotel_id": get_hotel_id,
            "room_number": room_number,
        })
        booking_id = create.json()["id"]

        response = await authorized_client.patch(f"/booking/{booking_id}")
        assert response.status_code == 403