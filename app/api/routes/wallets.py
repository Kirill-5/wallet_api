from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.wallet import Wallet
from app.schemas.wallet import WalletResponse, OperationRequest
from sqlalchemy import select
from uuid import UUID
from decimal import Decimal

print("Эндпоинт get_wallet загружен")

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])


@router.get("/{wallet_uuid}")
async def get_wallet(wallet_uuid: UUID, db: AsyncSession = Depends(get_db)):
    print(f"Searching for wallet with UUID: {wallet_uuid}")
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_uuid))
    my_wallet = result.scalar_one_or_none()
    if not my_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return WalletResponse(balance=my_wallet.balance)



@router.post("/{wallet_uuid}/operation")
async def new_operation(wallet_uuid: str, request: OperationRequest, db: AsyncSession = Depends(get_db)):
    # блокировка транзакции
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_uuid).with_for_update())
    my_wallet = result.scalar_one_or_none()
    if not my_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if request.operation_type == "DEPOSIT":
        my_wallet.balance += Decimal(request.amount)

    elif request.operation_type == "WITHDRAW":
        if my_wallet.balance < request.amount:
            raise HTTPException(status_code=400, detail="Wallet balance is low")
        my_wallet.balance -= Decimal(request.amount)

    else:
        raise HTTPException(status_code=404, detail="Operation type not supported")

    await db.commit()
    await db.refresh(my_wallet)
    return WalletResponse(balance=my_wallet.balance)