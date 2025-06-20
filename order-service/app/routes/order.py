from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from app.configs.database import get_db
from app.models import Order, OrderItem
from app.schemas.order import OrderCreate, OrderRead
from app.utils.verify_user import verify_user_token
from app.configs.config import settings
import httpx
import random
import aio_pika
import json
from app.utils.rate_limiter import rate_limit

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"]
)

async def get_current_user(request: Request):
    token_header = request.headers.get("Authorization")
    print(f"[DEBUG] Authorization header: {token_header}")
    if not token_header or not token_header.startswith("Bearer "):
        print("[DEBUG] Not authenticated: Missing or malformed Authorization header")
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = token_header.split(" ", 1)[1]
    print(f"[DEBUG] Extracted token: {token}")
    user = await verify_user_token(token)
    print(f"[DEBUG] Auth-service response: {user}")
    if not user:
        print("[DEBUG] Invalid or expired token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

def build_shipping_address(user):
    return ", ".join(
        filter(
            None,
            [
                user.get("street"),
                user.get("city"),
                user.get("province"),
                user.get("postal_code"),
                user.get("country"),
            ],
        )
    )

async def publish_order_created(order_data: dict):
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    message = aio_pika.Message(
        json.dumps(order_data).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )
    await channel.default_exchange.publish(
        message,
        routing_key="order.created"
    )
    await connection.close()
    print(f"[DEBUG] Published order.created event: {order_data}")

@router.post("/", response_model=OrderRead, status_code=201, dependencies=[Depends(rate_limit(times=5, seconds=60))])
async def create_order(order: OrderCreate, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Fetch product details and calculate totals
    items = []
    total_amount = 0
    order_items_data = []
    async with httpx.AsyncClient() as client:
        for item in order.items:
            product_resp = await client.get(f"{settings.PRODUCTS_API}/{item.product_id}")
            product = product_resp.json()
            print(f"[DEBUG] Product API response: {product}")
            if (
                not isinstance(product, dict)
                or "product" not in product
                or "price" not in product["product"]
            ):
                raise HTTPException(status_code=502, detail=f"Invalid product data for product_id {item.product_id}: {product}")
            price = product["product"]["price"]
            total_amt = price * item.quantity
            total_amount += total_amt
            items.append(OrderItem(product_id=item.product_id, quantity=item.quantity, total_amt=total_amt))
            order_items_data.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": price,
                "total_amt": total_amt
            })
    # Generate order_number (example: random 6-digit)
    order_number = random.randint(100000, 999999)
    shipping_address = build_shipping_address(user)
    db_order = Order(
        user_id=str(user["user_id"]),
        order_number=order_number,
        total_amount=str(total_amount),
        shipping_address=shipping_address,
        items=items
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Publish event for email notification
    await publish_order_created({
        "order_number": db_order.order_number,
        "user_email": user["email"],
        "user_name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
        "total_amount": db_order.total_amount,
        "items": order_items_data,
        "payment_method": db_order.payment_method
    })

    return db_order

@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.exec(select(Order).where(Order.id == order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/", response_model=list[OrderRead])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.exec(select(Order)).all()
    return orders