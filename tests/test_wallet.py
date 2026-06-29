import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import SessionLocal
from app.models.wallet import Wallet
import asyncio
import uuid

#получение кошелька
@pytest.mark.asyncio
async def test_get_wallet():
    wallet_id = uuid.uuid4()

    async with SessionLocal() as session:
        wallet = Wallet(id=wallet_id, balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/wallets/{wallet_id}")

    assert response.status_code == 200
    assert response.json()["balance"] == 100


#пополнение кошелька
@pytest.mark.asyncio
async def test_wallet_deposit():
    wallet_id = uuid.uuid4()

    async with SessionLocal() as session:
        wallet = Wallet(id=wallet_id, balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": 50}
        )

    assert response.status_code == 200
    assert response.json()["balance"] == 150


#снятие с кошелька
@pytest.mark.asyncio
async def test_wallet_withdraw():
    wallet_id = uuid.uuid4()

    async with SessionLocal() as session:
        wallet = Wallet(id=wallet_id, balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": 50}
        )

    assert response.status_code == 200
    assert response.json()["balance"] == 50


#снятие с кошелька при недостатке средств
@pytest.mark.asyncio
async def test_wallet_withdraw_insufficient_funds():
    wallet_id = uuid.uuid4()

    async with SessionLocal() as session:
        wallet = Wallet(id=wallet_id, balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": 200}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Wallet balance is low"


#неверный тип операции
@pytest.mark.asyncio
async def test_wallet_invalid_operation():
    wallet_id = uuid.uuid4()

    async with SessionLocal() as session:
        wallet = Wallet(id=wallet_id, balance=100)
        session.add(wallet)
        await session.commit()


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "TRANSFER", "amount": 200}
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Operation type not supported"




# два параллельных запроса на снятие
@pytest.mark.asyncio
async def test_wallet_transaction():
    wallet_id = uuid.uuid4()

    async with SessionLocal() as session:
        wallet = Wallet(id=wallet_id, balance=100)
        session.add(wallet)
        await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        responses = await asyncio.gather(
            ac.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 80}),
            ac.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 80})
        )

    assert responses[0].status_code == 200
    assert responses[1].status_code == 400



