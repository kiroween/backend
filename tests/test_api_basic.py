"""Basic API tests to verify the application works"""
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app
from app.models.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert "data" in data
    assert "result" in data["data"]


def test_get_empty_graveyard():
    """Test getting graveyard when no tombstones exist"""
    response = client.get("/api/graveyard")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert data["data"]["result"] == []


def test_create_tombstone():
    """Test creating a new tombstone"""
    future_date = (date.today() + timedelta(days=30)).isoformat()
    
    payload = {
        "title": "Test Memory",
        "content": "This is a test memory",
        "unlock_date": future_date
    }
    
    response = client.post("/api/tombstones", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == 201
    assert "data" in data
    assert "result" in data["data"]
    assert data["data"]["result"]["title"] == "Test Memory"
    assert data["data"]["result"]["is_unlocked"] is False
    assert "days_remaining" in data["data"]["result"]


def test_create_tombstone_with_past_date():
    """Test that creating tombstone with past date fails"""
    past_date = (date.today() - timedelta(days=1)).isoformat()
    
    payload = {
        "title": "Test Memory",
        "content": "This is a test memory",
        "unlock_date": past_date
    }
    
    response = client.post("/api/tombstones", json=payload)
    assert response.status_code == 400


def test_get_tombstone():
    """Test getting a specific tombstone"""
    # First create a tombstone
    future_date = (date.today() + timedelta(days=30)).isoformat()
    payload = {
        "title": "Test Memory",
        "content": "This is a test memory",
        "unlock_date": future_date
    }
    
    create_response = client.post("/api/tombstones", json=payload)
    tombstone_id = create_response.json()["data"]["result"]["id"]
    
    # Now get it
    response = client.get(f"/api/tombstones/{tombstone_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == 200
    assert data["data"]["result"]["id"] == tombstone_id
    assert "content" not in data["data"]["result"]  # Should be locked
    assert "days_remaining" in data["data"]["result"]


def test_get_nonexistent_tombstone():
    """Test getting a tombstone that doesn't exist"""
    response = client.get("/api/tombstones/99999")
    assert response.status_code == 404
