"""
Test fixtures and configuration for integration tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, get_db
import os

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Cleanup
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up all tables
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()

@pytest.fixture(scope="module")
def test_client(test_engine):
    """Create test client with dependency override."""
    from api import app
    
    # Override database dependency
    def override_get_db():
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(test_client):
    """Create a test user and return credentials."""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "user"
        }
    )
    assert response.status_code == 201
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "data": response.json()
    }

@pytest.fixture
def test_admin(test_client):
    """Create a test admin user."""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "adminpass123",
            "role": "admin"
        }
    )
    assert response.status_code == 201
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpass123",
        "data": response.json()
    }

@pytest.fixture
def auth_token(test_client, test_user):
    """Get auth token for test user."""
    response = test_client.post(
        "/api/v1/auth/login",
        params={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def admin_token(test_client, test_admin):
    """Get auth token for admin user."""
    response = test_client.post(
        "/api/v1/auth/login",
        params={
            "username": test_admin["username"],
            "password": test_admin["password"]
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def admin_headers(admin_token):
    """Get admin authorization headers."""
    return {"Authorization": f"Bearer {admin_token}"}
