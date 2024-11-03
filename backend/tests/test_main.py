# test_main.py

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, Base, get_db

# Set up a test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create a new engine instance
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Override the `get_db` dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Instantiate the TestClient with the FastAPI app
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_database():
    """Set up and tear down the database before and after each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_short_url():
    """Test creating a short URL."""
    response = client.post(
        "/shorten",
        json={"url": "http://example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert "original_url" in data
    assert data["original_url"] == "http://example.com/"
    assert data["visits_count"] == 0

def test_create_invalid_url():
    """Test creating a short URL with an invalid URL."""
    response = client.post(
        "/shorten",
        json={"url": "not-a-valid-url"}
    )
    assert response.status_code == 422

def test_duplicate_url():
    """Test that the same short URL is returned for duplicate original URLs."""
    # First request
    response1 = client.post(
        "/shorten",
        json={"url": "http://example.com/test"}
    )
    assert response1.status_code == 200

    # Second request with the same URL
    response2 = client.post(
        "/shorten",
        json={"url": "http://example.com/test"}
    )
    assert response2.status_code == 200

    # Check if the same short URL is returned
    assert response1.json()["short_url"] == response2.json()["short_url"]

def test_redirect():
    """Test redirection to the original URL."""
    # Create a short URL
    create_response = client.post(
        "/shorten",
        json={"url": "http://example.com/redirect-test"}
    )
    assert create_response.status_code == 200

    short_code = create_response.json()["short_url"].split("/")[-1]

    # Test redirection
    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "http://example.com/redirect-test"

def test_nonexistent_url():
    """Test accessing a nonexistent short code."""
    response = client.get("/nonexistent", follow_redirects=False)
    assert response.status_code == 404

def test_visit_counter():
    """Test that the visit counter increments upon accessing the short URL."""
    # Create a short URL
    create_response = client.post(
        "/shorten",
        json={"url": "http://example.com/counter-test"}
    )
    assert create_response.status_code == 200

    short_code = create_response.json()["short_url"].split("/")[-1]

    # Check initial visit count
    stats_response = client.get(f"/stats/{short_code}")
    assert stats_response.status_code == 200
    assert stats_response.json()["visits_count"] == 0

    # Access the short URL
    client.get(f"/{short_code}", follow_redirects=False)

    # Verify that the visit count has incremented
    stats_response = client.get(f"/stats/{short_code}")
    assert stats_response.status_code == 200
    assert stats_response.json()["visits_count"] == 1

def test_stats_nonexistent_url():
    """Test retrieving stats for a nonexistent short code."""
    response = client.get("/stats/nonexistent")
    assert response.status_code == 404

def test_url_length():
    """Test that the generated short code has the expected length."""
    response = client.post(
        "/shorten",
        json={"url": "http://example.com"}
    )
    assert response.status_code == 200
    short_code = response.json()["short_url"].split("/")[-1]
    expected_length = int(os.getenv("SHORT_URL_LENGTH", 6))
    assert len(short_code) == expected_length

def test_multiple_visits():
    """Test that the visit counter accurately reflects multiple visits."""
    # Create a short URL
    response = client.post(
        "/shorten",
        json={"url": "http://example.com/multiple-visits"}
    )
    assert response.status_code == 200
    short_code = response.json()["short_url"].split("/")[-1]

    # Access the short URL multiple times
    visits = 5
    for _ in range(visits):
        client.get(f"/{short_code}", follow_redirects=False)

    # Verify the visit count
    stats_response = client.get(f"/stats/{short_code}")
    assert stats_response.status_code == 200
    assert stats_response.json()["visits_count"] == visits

def test_special_characters_in_url():
    """Test handling of URLs with special characters."""
    test_url = "http://example.com/path?param=value&special=!@#$%^&*()"
    response = client.post(
        "/shorten",
        json={"url": test_url}
    )
    assert response.status_code == 200
    assert response.json()["original_url"] == test_url

def test_very_long_url():
    """Test handling of very long URLs."""
    long_path = "a" * 500  # URL with a long path
    test_url = f"http://example.com/{long_path}"
    response = client.post(
        "/shorten",
        json={"url": test_url}
    )
    assert response.status_code == 200
    assert response.json()["original_url"] == test_url
