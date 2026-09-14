from pydantic import BaseModel, Field


class SaleLineIn(BaseModel):
    product_id: int
    qty: float = Field(gt=0)
    unit_price: float | None = None
    discount: float = 0


class SalePaymentIn(BaseModel):
    method: str  # CASH, CARD, TRANSFER, CHECK, CREDIT, OTHER
    amount: float = Field(gt=0)
    reference: str | None = None


class SaleCreate(BaseModel):
    customer_id: int | None = None
    branch_id: int | None = None
    cash_session_id: int | None = None
    discount_global: float = 0
    notes: str | None = None
    ecf_type: str | None = None  # E32 consumidor final, E31 crédito fiscal...
    items: list[SaleLineIn]
    payments: list[SalePaymentIn]


class QuoteCreate(BaseModel):
    customer_id: int | None = None
    items: list[SaleLineIn]
    discount_global: float = 0
