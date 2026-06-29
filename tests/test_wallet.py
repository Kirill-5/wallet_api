import pytest
from httpx import AsyncClient
from app.main import app
from app.db.database import SessionLocal
from app.models.wallet import Wallet
import asyncio

#получение кошелька
@pytest.mark.asyncio
async def test_get_wallet():
    async with SessionLocal() as session:
        wallet = Wallet(id="123e4567-e89b-12d3-a456-426614174000", balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == 200
    assert response.json()["balance"] == 100


#пополнение кошелька
@pytest.mark.asyncio
async def test_wallet_deposit():
    async with SessionLocal() as session:
        wallet = Wallet(id="123e4567-e89b-12d3-a456-426614174000", balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(app=app , base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation",
            json={"operation_type": "DEPOSIT", "amount": 50}
        )

    assert response.status_code == 200
    assert response.json()["balance"] == 150


#снятие с кошелька
@pytest.mark.asyncio
async def test_wallet_withdraw():
    async with SessionLocal() as session:
        wallet = Wallet(id="123e4567-e89b-12d3-a456-426614174000", balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(app=app , base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation",
            json={"operation_type": "WITHDRAW", "amount": 50}
        )

    assert response.status_code == 200
    assert response.json()["balance"] == 50


#снятие с кошелька при недостатке средств
@pytest.mark.asyncio
async def test_wallet_withdraw():
    async with SessionLocal() as session:
        wallet = Wallet(id="123e4567-e89b-12d3-a456-426614174000", balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(app=app , base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation",
            json={"operation_type": "WITHDRAW", "amount": 200}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Wallet balance is low"


#неверный тип операции
@pytest.mark.asyncio
async def test_wallet_withdraw():
    async with SessionLocal() as session:
        wallet = Wallet(id="123e4567-e89b-12d3-a456-426614174000", balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(app=app , base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation",
            json={"operation_type": "TRANSFER", "amount": 200}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Operation type not supported"




# два параллельных запроса на снятие
@pytest.mark.asyncio
async def test_wallet_transaction():
    async with SessionLocal() as session:
        wallet = Wallet(id="123e4567-e89b-12d3-a456-426614174000", balance=100)
        session.add(wallet)
        await session.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        responses = await asyncio.gather(
            ac.post("/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation", json={"operation_type": "WITHDRAW", "amount": 80}),
            ac.post("/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation", json={"operation_type": "WITHDRAW", "amount": 80})
        )

    assert responses[0].status_code == 200
    assert responses[1].status_code == 400



