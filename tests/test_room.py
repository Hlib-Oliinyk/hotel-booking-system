import pytest


HOTEL_PAYLOAD = {
    "title": "Grand Hotel",
    "location": "Kyiv"
}

ROOM_PAYLOAD = {
    "hotel_id": None,
    "number": "101",
    "room_type": "standard",
    "price_per_night": 1500,
    "description": "Cozy room"
}

ROOM_PAYLOAD_2 = {
    "hotel_id": None,
    "number": "102",
    "room_type": "suite",
    "price_per_night": 3000,
    "description": "Luxury suite"
}

UPDATED_ROOM_PAYLOAD = {
    "number": "101-UPDATED",
    "room_type": "deluxe",
    "price_per_night": 2000,
    "description": "Updated description",
    "is_available": False
}

async def create_hotel(admin_client):
    resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
    assert resp.status_code == 200
    return resp.json()["id"]


async def create_room(admin_client, hotel_id, payload_override=None):
    payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id}
    if payload_override:
        payload.update(payload_override)
    resp = await admin_client.post("/rooms", json=payload)
    assert resp.status_code == 201
    return resp.json()


class TestGetRooms:

    @pytest.mark.asyncio
    async def test_get_rooms_returns_list(self, async_client):
        response = await async_client.get("/rooms")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_rooms_no_auth_required(self, async_client):
        response = await async_client.get("/rooms")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_rooms_contains_created_room(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await async_client.get("/rooms")
        assert response.status_code == 200
        ids = [r["id"] for r in response.json()]
        assert room["id"] in ids

    @pytest.mark.asyncio
    async def test_get_rooms_filter_by_hotel_id(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await async_client.get("/rooms", params={"hotel_id": hotel_id})
        assert response.status_code == 200
        data = response.json()
        assert all(r["hotel_id"] == hotel_id for r in data)
        ids = [r["id"] for r in data]
        assert room["id"] in ids

    @pytest.mark.asyncio
    async def test_get_rooms_filter_no_match(self, async_client):
        response = await async_client.get("/rooms", params={"hotel_id": 999999})
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_rooms_returns_correct_schema(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        await create_room(admin_client, hotel_id)

        response = await async_client.get("/rooms")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert set(data[0].keys()) >= {"id", "hotel_id", "number", "room_type", "price_per_night", "is_available"}


class TestGetRoomById:

    @pytest.mark.asyncio
    async def test_get_room_by_id_success(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await async_client.get(f"/rooms/{room['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == room["id"]
        assert data["number"] == room["number"]

    @pytest.mark.asyncio
    async def test_get_room_by_id_no_auth_required(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await async_client.get(f"/rooms/{room['id']}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_room_by_id_not_found(self, async_client):
        response = await async_client.get("/rooms/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_room_by_id_invalid_id(self, async_client):
        response = await async_client.get("/rooms/abc")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_room_by_id_returns_correct_schema(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await async_client.get(f"/rooms/{room['id']}")
        assert response.status_code == 200
        assert set(response.json().keys()) >= {"id", "hotel_id", "number", "room_type", "price_per_night", "is_available"}


class TestCreateRoom:

    @pytest.mark.asyncio
    async def test_create_room_success(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["number"] == payload["number"]
        assert data["room_type"] == payload["room_type"]
        assert data["price_per_night"] == payload["price_per_night"]
        assert data["hotel_id"] == hotel_id
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_room_without_auth(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id}

        response = await async_client.post("/rooms", json=payload)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_room_as_regular_user(self, authorized_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id}

        response = await authorized_client.post("/rooms", json=payload)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_room_missing_hotel_id(self, admin_client):
        payload = {"number": "101", "room_type": "standard", "price_per_night": 1500}
        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_room_missing_number(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {"hotel_id": hotel_id, "room_type": "standard", "price_per_night": 1500}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_room_missing_room_type(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {"hotel_id": hotel_id, "number": "101", "price_per_night": 1500}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_room_missing_price_per_night(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {"hotel_id": hotel_id, "number": "101", "room_type": "standard"}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_room_price_zero_invalid(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id, "price_per_night": 0}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_room_price_negative_invalid(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id, "price_per_night": -100}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_room_empty_body(self, admin_client):
        response = await admin_client.post("/rooms", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_room_nonexistent_hotel(self, admin_client):
        payload = {**ROOM_PAYLOAD, "hotel_id": 999999}
        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_room_optional_description_omitted(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {"hotel_id": hotel_id, "number": "201", "room_type": "standard", "price_per_night": 1000}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_room_returns_correct_schema(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 201
        assert set(response.json().keys()) >= {"id", "hotel_id", "number", "room_type", "price_per_night", "is_available"}

    @pytest.mark.asyncio
    async def test_create_room_is_available_defaults_true(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        payload = {**ROOM_PAYLOAD, "hotel_id": hotel_id}

        response = await admin_client.post("/rooms", json=payload)
        assert response.status_code == 201
        assert response.json()["is_available"] is True


class TestPatchRoom:

    @pytest.mark.asyncio
    async def test_patch_room_success(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await admin_client.patch(f"/rooms/{room['id']}", json=UPDATED_ROOM_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == room["id"]
        assert data["number"] == UPDATED_ROOM_PAYLOAD["number"]
        assert data["room_type"] == UPDATED_ROOM_PAYLOAD["room_type"]
        assert data["price_per_night"] == UPDATED_ROOM_PAYLOAD["price_per_night"]
        assert data["is_available"] == UPDATED_ROOM_PAYLOAD["is_available"]

    @pytest.mark.asyncio
    async def test_patch_room_partial_price(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await admin_client.patch(f"/rooms/{room['id']}", json={"price_per_night": 9999})
        assert response.status_code == 200
        assert response.json()["price_per_night"] == 9999
        assert response.json()["number"] == room["number"]

    @pytest.mark.asyncio
    async def test_patch_room_partial_is_available(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await admin_client.patch(f"/rooms/{room['id']}", json={"is_available": False})
        assert response.status_code == 200
        assert response.json()["is_available"] is False

    @pytest.mark.asyncio
    async def test_patch_room_price_zero_invalid(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await admin_client.patch(f"/rooms/{room['id']}", json={"price_per_night": 0})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_patch_room_without_auth(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await async_client.patch(f"/rooms/{room['id']}", json=UPDATED_ROOM_PAYLOAD)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_patch_room_as_regular_user(self, authorized_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await authorized_client.patch(f"/rooms/{room['id']}", json=UPDATED_ROOM_PAYLOAD)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_patch_room_not_found(self, admin_client):
        response = await admin_client.patch("/rooms/999999", json=UPDATED_ROOM_PAYLOAD)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_patch_room_invalid_id(self, admin_client):
        response = await admin_client.patch("/rooms/abc", json=UPDATED_ROOM_PAYLOAD)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_patch_room_empty_body_still_ok(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await admin_client.patch(f"/rooms/{room['id']}", json={})
        assert response.status_code == 200
        assert response.json()["id"] == room["id"]

    @pytest.mark.asyncio
    async def test_patch_room_returns_correct_schema(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await admin_client.patch(f"/rooms/{room['id']}", json=UPDATED_ROOM_PAYLOAD)
        assert response.status_code == 200
        assert set(response.json().keys()) >= {"id", "hotel_id", "number", "room_type", "price_per_night", "is_available"}


class TestDeleteRoom:

    @pytest.mark.asyncio
    async def test_delete_room_success(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await admin_client.delete(f"/rooms/{room['id']}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_room_actually_removed(self, admin_client, async_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        await admin_client.delete(f"/rooms/{room['id']}")

        get_resp = await async_client.get(f"/rooms/{room['id']}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_room_without_auth(self, async_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await async_client.delete(f"/rooms/{room['id']}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_room_as_regular_user(self, authorized_client, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        response = await authorized_client.delete(f"/rooms/{room['id']}")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_room_not_found(self, admin_client):
        response = await admin_client.delete("/rooms/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_room_invalid_id(self, admin_client):
        response = await admin_client.delete("/rooms/abc")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_room_twice(self, admin_client):
        hotel_id = await create_hotel(admin_client)
        room = await create_room(admin_client, hotel_id)

        await admin_client.delete(f"/rooms/{room['id']}")
        response = await admin_client.delete(f"/rooms/{room['id']}")
        assert response.status_code == 404