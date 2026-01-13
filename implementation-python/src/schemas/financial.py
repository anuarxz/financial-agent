"""Financial data schemas."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class TableName(str, Enum):
    """Available database tables."""

    EXPENSES = "expenses"
    SAVINGS = "savings"
    INVESTMENTS = "investments"


class ExpenseCreate(BaseModel):
    """Schema for creating an expense."""

    amount: Decimal = Field(..., gt=0, description="Expense amount")
    category: str = Field(..., min_length=1, max_length=100, description="Expense category")
    description: Optional[str] = Field(None, max_length=500, description="Expense description")


class Expense(ExpenseCreate):
    """Schema for expense with database fields."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SavingCreate(BaseModel):
    """Schema for creating a saving."""

    amount: Decimal = Field(..., gt=0, description="Saving amount")
    goal: str = Field(..., min_length=1, max_length=100, description="Saving goal")
    description: Optional[str] = Field(None, max_length=500, description="Saving description")


class Saving(SavingCreate):
    """Schema for saving with database fields."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvestmentCreate(BaseModel):
    """Schema for creating an investment."""

    amount: Decimal = Field(..., gt=0, description="Investment amount")
    asset_type: str = Field(..., min_length=1, max_length=100, description="Type of asset")
    description: Optional[str] = Field(None, max_length=500, description="Investment description")


class Investment(InvestmentCreate):
    """Schema for investment with database fields."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


FinancialRecord = Union[Expense, Saving, Investment]
