import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_db
from ..models.orders import (
    CursorPaginationInfo,
    Order,
    OrderCount,
    OrderListCursorResponse,
    OrderListResponse,
    OrderRead,
    OrderSample,
    OrderStatusUpdate,
    OrderStatusUpdateResponse,
    PaginationInfo,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/count", response_model=OrderCount, summary="Get total order count")
async def get_order_count(db: AsyncSession = Depends(get_async_db)):
    """Get the total number of orders in the database."""
    try:
        stmt = select(func.count(Order.o_orderkey))
        result = await db.execute(stmt)
        count = result.scalar()
        return OrderCount(total_orders=count)
    except Exception as e:
        logger.error(f"Error getting order count: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve order count")


@router.get("/sample", response_model=OrderSample, summary="Get 5 random order keys")
async def get_sample_orders(db: AsyncSession = Depends(get_async_db)):
    """Get 5 random order keys for testing."""
    try:
        stmt = select(Order.o_orderkey).limit(5)
        result = await db.execute(stmt)
        order_keys = result.scalars().all()
        return OrderSample(sample_order_keys=order_keys)
    except Exception as e:
        logger.error(f"Error getting sample orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sample orders")


@router.get(
    "/pages",
    response_model=OrderListResponse,
    summary="Get orders with page-based pagination",
)
async def get_orders_by_page(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(
        100, ge=1, le=1000, description="Number of records per page (max 1000)"
    ),
    include_count: bool = Query(
        True, description="Include total count for pagination info"
    ),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get orders using traditional page-based pagination.

    **Best for:**
    - Small to medium datasets
    - Building traditional pagination UI with page numbers
    - When users need to jump to specific pages

    **Usage:**
    - `/orders/pages?page=1&page_size=100`
    - `/orders/pages?page=5&page_size=50&include_count=false`
    """
    try:
        if include_count:
            count_stmt = select(func.count(Order.o_orderkey))
            count_result = await db.execute(count_stmt)
            total_count = count_result.scalar()
            total_pages = (total_count + page_size - 1) // page_size
        else:
            total_count = -1
            total_pages = -1

        offset = (page - 1) * page_size
        stmt = (
            select(
                Order.o_orderkey,
                Order.o_custkey,
                Order.o_orderstatus,
                Order.o_totalprice,
                Order.o_orderdate,
                Order.o_orderpriority,
                Order.o_clerk,
                Order.o_shippriority,
                Order.o_comment,
            )
            .order_by(Order.o_orderkey)
            .offset(offset)
            .limit(page_size + 1)  # Get one extra to check has_next
        )

        result = await db.execute(stmt)
        all_orders = result.all()

        has_next = len(all_orders) > page_size
        orders_data = all_orders[:page_size]
        has_previous = page > 1

        orders = [
            OrderRead(
                o_orderkey=row[0],
                o_custkey=row[1],
                o_orderstatus=row[2],
                o_totalprice=row[3],
                o_orderdate=row[4],
                o_orderpriority=row[5],
                o_clerk=row[6],
                o_shippriority=row[7],
                o_comment=row[8],
            )
            for row in orders_data
        ]

        next_cursor = orders[-1].o_orderkey if orders and has_next else None
        previous_cursor = (
            orders[0].o_orderkey - page_size if orders and has_previous else None
        )

        pagination_info = PaginationInfo(
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count,
            has_next=has_next,
            has_previous=has_previous,
            next_cursor=next_cursor,
            previous_cursor=max(0, previous_cursor) if previous_cursor else None,
        )

        return OrderListResponse(orders=orders, pagination=pagination_info)

    except Exception as e:
        logger.error(f"Error getting page-based orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orders")


@router.get(
    "/stream",
    response_model=OrderListCursorResponse,
    summary="Get orders with cursor-based pagination",
)
async def get_orders_by_cursor(
    cursor: int = Query(
        0, ge=0, description="Start after this order key (0 for beginning)"
    ),
    page_size: int = Query(
        100, ge=1, le=1000, description="Number of records to fetch (max 1000)"
    ),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get orders using efficient cursor-based pagination.

    **Best for:**
    - Large datasets (millions of records)
    - High-performance applications
    - Infinite scroll UIs
    - Real-time data feeds

    **Usage:**
    - First page: `/orders/stream?cursor=0&page_size=100`
    - Next page: `/orders/stream?cursor=100&page_size=100`
    - Jump to key: `/orders/stream?cursor=12345&page_size=100` (shows records after key 12345)
    """
    try:
        stmt = (
            select(
                Order.o_orderkey,
                Order.o_custkey,
                Order.o_orderstatus,
                Order.o_totalprice,
                Order.o_orderdate,
                Order.o_orderpriority,
                Order.o_clerk,
                Order.o_shippriority,
                Order.o_comment,
            )
            .where(Order.o_orderkey > cursor)
            .order_by(Order.o_orderkey)
            .limit(page_size + 1)  # Get one extra to check has_next
        )

        result = await db.execute(stmt)
        all_orders = result.all()

        has_next = len(all_orders) > page_size
        orders_data = all_orders[:page_size]
        has_previous = cursor > 0

        orders = [
            OrderRead(
                o_orderkey=row[0],
                o_custkey=row[1],
                o_orderstatus=row[2],
                o_totalprice=row[3],
                o_orderdate=row[4],
                o_orderpriority=row[5],
                o_clerk=row[6],
                o_shippriority=row[7],
                o_comment=row[8],
            )
            for row in orders_data
        ]

        next_cursor = orders[-1].o_orderkey if orders and has_next else None
        previous_cursor = max(0, cursor - page_size) if has_previous else None

        pagination_info = CursorPaginationInfo(
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        return OrderListCursorResponse(orders=orders, pagination=pagination_info)

    except Exception as e:
        logger.error(f"Error getting cursor-based orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orders")


@router.get("/{order_key}", response_model=OrderRead, summary="Get an order by its key")
async def read_order(
    order_key: int, response: Response, db: AsyncSession = Depends(get_async_db)
):
    """
    Fetch a single order by its key, returning all order fields.
    """
    try:
        if order_key <= 0:
            raise HTTPException(status_code=400, detail="Invalid order key provided")

        stmt = select(Order).where(Order.o_orderkey == order_key)
        result = await db.execute(stmt)
        order = result.scalars().first()

        if not order:
            logger.info(f"Order not found: {order_key}")
            raise HTTPException(
                status_code=404, detail=f"Order with key '{order_key}' not found"
            )

        return order

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching order {order_key}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")


@router.post(
    "/{order_key}/status",
    response_model=OrderStatusUpdateResponse,
    summary="Update order status",
)
async def update_order_status(
    order_key: int,
    status_data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update the status for a specific order.

    - **order_key**: The key of the order to update
    - **o_orderstatus**: The new status to assign
    """
    try:
        if order_key <= 0:
            raise HTTPException(status_code=400, detail="Invalid order key provided")

        check_stmt = select(Order).where(Order.o_orderkey == order_key)
        check_result = await db.execute(check_stmt)
        existing_order = check_result.scalars().first()

        if not existing_order:
            logger.info(f"Order not found for update: {order_key}")
            raise HTTPException(
                status_code=404, detail=f"Order with key '{order_key}' not found"
            )

        existing_order.o_orderstatus = status_data.o_orderstatus
        await db.commit()
        await db.refresh(existing_order)

        logger.info(
            f"Successfully updated order {order_key} status to {status_data.o_orderstatus}"
        )

        return OrderStatusUpdateResponse(
            o_orderkey=order_key,
            o_orderstatus=status_data.o_orderstatus,
            message="Order status updated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status for order {order_key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order status")
