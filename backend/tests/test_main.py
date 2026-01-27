import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db, Base

# Test SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.mark.asyncio
async def test_read_main():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Pro-NLP AI Recruitment Platform API", "docs": "/docs"}

@pytest.mark.asyncio
async def test_auth_me_placeholder():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/auth/me")
    assert response.status_code == 200
    assert "email" in response.json()

@pytest.mark.asyncio
async def test_list_recruits_placeholder():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/recruits/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "meta" in data

@pytest.mark.asyncio
async def test_get_recruit_detail():
    # Detail search with ID 1 might fail if no data exists, but endpoint should be callable
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/recruits/1")
    # If not found, it returns 404 which is a valid API response
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_kakao_callback_placeholder():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/auth/kakao/callback?code=test_code")
    assert response.status_code == 200
    assert response.json()["code"] == "test_code"

@pytest.mark.asyncio
async def test_list_portfolios_placeholder():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/portfolios/")
    assert response.status_code == 200
    assert "items" in response.json()

@pytest.mark.asyncio
async def test_analyze_portfolio_placeholder():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/portfolios/analyze", json={"source": "github", "type": "link"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_list_cover_letters_placeholder():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/cover-letters/")
    assert response.status_code == 200
    assert "items" in response.json()

@pytest.mark.asyncio
async def test_generate_cover_letter_placeholder():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/cover-letters/generate", json={
            "recruitId": 1,
            "portfolioIds": [1],
            "question": "지원동기",
            "tone": "professional"
        })
    assert response.status_code == 200
    assert "result" in response.json()

@pytest.mark.asyncio
async def test_swagger_docs_accessible():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/docs")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_redoc_docs_accessible():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/redoc")
    assert response.status_code == 200
