import json
from apps.authtoken.models import ApiToken


def test_login_success(client, test_user):
    """Successful login returns a token and creates an ApiToken."""
    payload = {
        "username": "testuser",
        "password": "testpass123",
    }

    resp = client.post("/api/auth/login", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data

    # Token persisted
    assert ApiToken.objects.filter(user__username="testuser", token=data["token"]).exists()


def test_login_failure(client, test_user):
    """Invalid credentials return 401 with error payload."""
    payload = {
        "username": "testuser",
        "password": "wrongpassword",
    }

    resp = client.post("/api/auth/login", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 401
    data = resp.json()
    assert data.get("code") == "401"
    assert "Invalid username" in data.get("description", "")
