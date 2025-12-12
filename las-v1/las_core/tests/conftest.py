"""
Test fixtures and configuration for integration tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from services.db.postgres import get_db
from unittest.mock import Mock, patch, AsyncMock
import os

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# API Key for tests (used by security middleware)
TEST_API_KEY = os.getenv("LAS_API_KEY") or "las-secret-key"

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


class AuthenticatedTestClient:
    """Wrapper around TestClient that automatically includes API key header."""
    
    def __init__(self, client: TestClient):
        self._client = client
        self._default_headers = {"X-API-Key": TEST_API_KEY}
    
    def _merge_headers(self, headers=None):
        merged = self._default_headers.copy()
        if headers:
            merged.update(headers)
        return merged
    
    def get(self, url, **kwargs):
        kwargs["headers"] = self._merge_headers(kwargs.get("headers"))
        return self._client.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        kwargs["headers"] = self._merge_headers(kwargs.get("headers"))
        return self._client.post(url, **kwargs)
    
    def put(self, url, **kwargs):
        kwargs["headers"] = self._merge_headers(kwargs.get("headers"))
        return self._client.put(url, **kwargs)
    
    def patch(self, url, **kwargs):
        kwargs["headers"] = self._merge_headers(kwargs.get("headers"))
        return self._client.patch(url, **kwargs)
    
    def delete(self, url, **kwargs):
        kwargs["headers"] = self._merge_headers(kwargs.get("headers"))
        return self._client.delete(url, **kwargs)


@pytest.fixture(scope="module")
def test_client(test_engine):
    """Create test client with dependency override and API key auth."""
    # Mock heavy services that cause timeouts during startup
    mock_interaction_service = Mock()
    mock_interaction = Mock()
    mock_interaction_service.get_interaction.return_value = mock_interaction
    mock_interaction.last_answer = "Test answer"
    mock_interaction.last_reasoning = "Test reasoning"
    mock_interaction.last_success = True
    mock_interaction.current_agent = Mock()
    mock_interaction.current_agent.agent_name = "TestAgent"
    mock_interaction.current_agent.get_blocks_result.return_value = []
    
    with patch('services.interaction_service.InteractionService', return_value=mock_interaction_service), \
         patch('services.interaction_service.get_interaction_service', return_value=mock_interaction_service), \
         patch('services.db.postgres.init_db', new_callable=AsyncMock):
        
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
            # Wrap client to include API key header automatically
            yield AuthenticatedTestClient(client)
        
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
    assert response.status_code == 201, f"Registration failed: {response.text}"
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
    assert response.status_code == 201, f"Admin registration failed: {response.text}"
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
    assert response.status_code == 200, f"Login failed: {response.text}"
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
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers."""
    return {"Authorization": f"Bearer {auth_token}", "X-API-Key": TEST_API_KEY}

@pytest.fixture
def admin_headers(admin_token):
    """Get admin authorization headers."""
    return {"Authorization": f"Bearer {admin_token}", "X-API-Key": TEST_API_KEY}
