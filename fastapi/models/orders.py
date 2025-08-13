from datetime import date
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class OrderBase(SQLModel):
    o_custkey: int
    o_orderstatus: str
    o_totalprice: Decimal = Field(max_digits=18, decimal_places=2)
    o_orderdate: date
    o_orderpriority: str
    o_clerk: str
    o_shippriority: int
    o_comment: str


class Order(OrderBase, table=True):
    __tablename__ = "orders_synced"
    __table_args__ = "public"
    o_orderkey: Optional[int] = Field(default=None, primary_key=True)


class OrderRead(OrderBase):
    o_orderkey: int


class OrderCount(SQLModel):
    total_orders: int


class OrderSample(SQLModel):
    sample_order_keys: list[int]


class OrderStatusUpdate(SQLModel):
    o_orderstatus: str


class OrderStatusUpdateResponse(SQLModel):
    o_orderkey: int
    o_orderstatus: str
    message: str


class OrderListResponse(SQLModel):
    orders: list[OrderRead]
    pagination: "PaginationInfo"


class PaginationInfo(SQLModel):
    page: int
    page_size: int
    total_pages: int
    total_count: int
    has_next: bool
    has_previous: bool
    next_cursor: int | None = None
    previous_cursor: int | None = None


class CursorPaginationInfo(SQLModel):
    page_size: int
    has_next: bool
    has_previous: bool
    next_cursor: int | None = None
    previous_cursor: int | None = None


class OrderListCursorResponse(SQLModel):
    orders: list[OrderRead]
    pagination: CursorPaginationInfo
