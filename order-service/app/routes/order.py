from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from app.configs.database import get_db
from app.models import Order, OrderItem
from app.schemas.order import OrderCreate, OrderRead
from app.utils.verify_user import verify_user_token
from app.configs.config import settings
import httpx
import random

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

@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(order: OrderCreate, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Fetch product details and calculate totals
    items = []
    total_amount = 0
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
    return db_order

@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.exec(select(Order).where(Order.id == order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
