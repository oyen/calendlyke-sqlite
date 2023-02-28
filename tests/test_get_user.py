import pytest
import json

from app import app

@pytest.fixture
def client():
    with app.app_context():
        with app.test_client() as client:
            yield client

def test_get_user_not_found(client):
    url = "/users/1"

    resp = client.get(url)
    assert resp.status_code == 200

    data = json.loads(resp.data.decode('utf8'))
    assert  data["error"] == "data not found"
