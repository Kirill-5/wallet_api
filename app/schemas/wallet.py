from pydantic import BaseModel
from decimal import Decimal



class WalletResponse(BaseModel):
    balance: int


class OperationRequest(BaseModel):
    operation_type: str
    amount: Decimal