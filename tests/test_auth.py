import pytest

from tests.data import TEST_USER, TEST_LOGIN


class TestRegister:

    @pytest.mark.asyncio
    async def test_register_success(self, async_client):
        response = await async_client.post("/auth/register", json=TEST_USER)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER["email"]
        assert "id" in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client):
        await async_client.post("/auth/register", json=TEST_USER)
        response = await async_client.post("/auth/register", json=TEST_USER)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client):
        response = await async_client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "secret-password"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_password(self, async_client):
        response = await async_client.post("/auth/register", json={
            "email": "test2@gmail.com"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_email(self, async_client):
        response = await async_client.post("/auth/register", json={
            "password": "secret-password"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_body(self, async_client):
        response = await async_client.post("/auth/register", json={})
        assert response.status_code == 422


class TestLogin:

    @pytest.mark.asyncio
    async def test_login_success(self, async_client):
        await async_client.post("/auth/register", json=TEST_USER)
        response = await async_client.post("/auth/login", json=TEST_LOGIN)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

    @pytest.mark.asyncio
    async def test_login_sets_cookies(self, async_client):
        await async_client.post("/auth/register", json=TEST_USER)
        response = await async_client.post("/auth/login", json=TEST_LOGIN)
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client):
        await async_client.post("/auth/register", json=TEST_USER)
        response = await async_client.post("/auth/login", json={
            "email": TEST_USER["email"],
            "password": "wrong-password"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_wrong_email(self, async_client):
        response = await async_client.post("/auth/login", json={
            "email": "nonexistent@gmail.com",
            "password": "secret-password"
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, async_client):
        response = await async_client.post("/auth/login", json={
            "email": "not-an-email",
            "password": "secret-password"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, async_client):
        response = await async_client.post("/auth/login", json={})
        assert response.status_code == 422


class TestLogout:

    @pytest.mark.asyncio
    async def test_logout_success(self, authorized_client):
        response = await authorized_client.delete("/auth/logout")
        assert response.status_code == 200
        assert response.json()["detail"] == "Logged out"

    @pytest.mark.asyncio
    async def test_logout_clears_cookies(self, authorized_client):
        response = await authorized_client.delete("/auth/logout")
        assert "access_token" not in response.cookies
        assert "refresh_token" not in response.cookies

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, async_client):
        response = await async_client.delete("/auth/logout")
        assert response.status_code in (200, 401)

    @pytest.mark.asyncio
    async def test_logout_twice(self, authorized_client):
        await authorized_client.delete("/auth/logout")
        response = await authorized_client.delete("/auth/logout")
        assert response.status_code in (200, 401)


class TestRefresh:

    @pytest.mark.asyncio
    async def test_refresh_success(self, authorized_client):
        response = await authorized_client.post("/auth/refresh")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

    @pytest.mark.asyncio
    async def test_refresh_sets_new_cookies(self, authorized_client):
        response = await authorized_client.post("/auth/refresh")
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_refresh_token_rotated(self, authorized_client):
        old_refresh = authorized_client.cookies.get("refresh_token")
        await authorized_client.post("/auth/refresh")
        new_refresh = authorized_client.cookies.get("refresh_token")
        assert old_refresh != new_refresh

    @pytest.mark.asyncio
    async def test_refresh_without_cookie(self, async_client):
        response = await async_client.post("/auth/refresh")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, async_client):
        async_client.cookies.set("refresh_token", "invalid-token")
        response = await async_client.post("/auth/refresh")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_after_logout(self, authorized_client):
        await authorized_client.delete("/auth/logout")
        response = await authorized_client.post("/auth/refresh")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_old_refresh_token_invalid_after_rotation(self, authorized_client):
        old_refresh = authorized_client.cookies.get("refresh_token")
        await authorized_client.post("/auth/refresh")

        authorized_client.cookies.set("refresh_token", old_refresh)
        response = await authorized_client.post("/auth/refresh")
        assert response.status_code == 401