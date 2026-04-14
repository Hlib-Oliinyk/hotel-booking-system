import pytest


HOTEL_PAYLOAD = {
    "title": "Grand Hotel",
    "location": "Kyiv"
}

HOTEL_PAYLOAD_2 = {
    "title": "Ocean View",
    "location": "Odesa"
}

UPDATED_HOTEL_PAYLOAD = {
    "title": "Grand Hotel Updated",
    "location": "Lviv"
}


class TestCreateHotel:

    @pytest.mark.asyncio
    async def test_create_hotel_success(self, admin_client):
        response = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == HOTEL_PAYLOAD["title"]
        assert data["location"] == HOTEL_PAYLOAD["location"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_hotel_without_auth(self, async_client):
        response = await async_client.post("/hotel", json=HOTEL_PAYLOAD)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_hotel_as_regular_user(self, authorized_client):
        response = await authorized_client.post("/hotel", json=HOTEL_PAYLOAD)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_hotel_missing_name(self, admin_client):
        response = await admin_client.post("/hotel", json={"location": "Kyiv"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_hotel_missing_location(self, admin_client):
        response = await admin_client.post("/hotel", json={"title": "Grand Hotel"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_hotel_empty_body(self, admin_client):
        response = await admin_client.post("/hotel", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_hotel_returns_correct_schema(self, admin_client):
        response = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) >= {"id", "title", "location"}


class TestGetHotels:

    @pytest.mark.asyncio
    async def test_get_hotels_returns_list(self, async_client):
        response = await async_client.get("/hotel")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_hotels_contains_created_hotel(self, async_client, admin_client):
        await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        response = await async_client.get("/hotel")
        assert response.status_code == 200
        titles = [h["title"] for h in response.json()]
        assert HOTEL_PAYLOAD["title"] in titles

    @pytest.mark.asyncio
    async def test_get_hotels_filter_by_location(self, async_client, admin_client):
        await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        await admin_client.post("/hotel", json=HOTEL_PAYLOAD_2)
        response = await async_client.get("/hotel", params={"location": "Odesa"})
        assert response.status_code == 200
        data = response.json()
        assert all("Odesa" in h["location"] for h in data)

    @pytest.mark.asyncio
    async def test_get_hotels_filter_no_match(self, async_client):
        response = await async_client.get("/hotel", params={"location": "NonExistentCity12345"})
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_hotels_no_auth_required(self, async_client):
        response = await async_client.get("/hotel")
        assert response.status_code == 200


class TestUpdateHotel:

    @pytest.mark.asyncio
    async def test_update_hotel_success(self, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await admin_client.put(f"/hotel/{hotel_id}", json=UPDATED_HOTEL_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == UPDATED_HOTEL_PAYLOAD["title"]
        assert data["location"] == UPDATED_HOTEL_PAYLOAD["location"]
        assert data["id"] == hotel_id

    @pytest.mark.asyncio
    async def test_update_hotel_without_auth(self, async_client, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await async_client.put(f"/hotel/{hotel_id}", json=UPDATED_HOTEL_PAYLOAD)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_hotel_as_regular_user(self, authorized_client, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await authorized_client.put(f"/hotel/{hotel_id}", json=UPDATED_HOTEL_PAYLOAD)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_hotel_not_found(self, admin_client):
        response = await admin_client.put("/hotel/999999", json=UPDATED_HOTEL_PAYLOAD)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_hotel_missing_name(self, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await admin_client.put(f"/hotel/{hotel_id}", json={"location": "Lviv"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_hotel_missing_location(self, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await admin_client.put(f"/hotel/{hotel_id}", json={"title": "New Name"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_hotel_invalid_id(self, admin_client):
        response = await admin_client.put("/hotel/abc", json=UPDATED_HOTEL_PAYLOAD)
        assert response.status_code == 422


class TestDeleteHotel:

    @pytest.mark.asyncio
    async def test_delete_hotel_success(self, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await admin_client.delete(f"/hotel/{hotel_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_hotel_actually_removed(self, admin_client, async_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]
        await admin_client.delete(f"/hotel/{hotel_id}")

        get_resp = await async_client.get("/hotel")
        ids = [h["id"] for h in get_resp.json()]
        assert hotel_id not in ids

    @pytest.mark.asyncio
    async def test_delete_hotel_without_auth(self, async_client, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await async_client.delete(f"/hotel/{hotel_id}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_hotel_as_regular_user(self, authorized_client, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        response = await authorized_client.delete(f"/hotel/{hotel_id}")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_hotel_not_found(self, admin_client):
        response = await admin_client.delete("/hotel/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_hotel_invalid_id(self, admin_client):
        response = await admin_client.delete("/hotel/abc")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_hotel_twice(self, admin_client):
        create_resp = await admin_client.post("/hotel", json=HOTEL_PAYLOAD)
        hotel_id = create_resp.json()["id"]

        await admin_client.delete(f"/hotel/{hotel_id}")
        response = await admin_client.delete(f"/hotel/{hotel_id}")
        assert response.status_code == 404