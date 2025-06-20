# E-commerce Order Management - Microservices Architecture

## System Overview
Building an Amazon-like order management system using external product API (fakestoreapi.in) with 4 microservices.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend/     │    │   Auth Service  │    │  Order Service  │
│   Mobile App    │◄──►│    (Port 8001)  │◄──►│   (Port 8003)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│External Product │    │     Redis       │    │    RabbitMQ     │
│API (fakestore)  │    │   (Caching)     │    │ (Message Queue) │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                               ┌─────────────────┐
                               │ Email Service   │
                               │   (Node.js)     │
                               │                 │
                               └─────────────────┘
```

## Service Architecture

### 1. Auth Service (Port 8001)
**Responsibility:** User management and JWT token generation

**Database Schema:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    street = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    is_default = Column(Boolean, default=False)
```

**API Endpoints:**
- `POST /register` - User registration
- `POST /login` - User login (returns JWT)
- `POST /verify-token` - Token verification (used by other services)
- `GET /user/{user_id}` - Get user details (for other services)
- `GET /user/{user_id}/addresses` - Get user addresses
- `POST /user/{user_id}/addresses` - Add new address

**JWT Token Structure:**
```python
# Token payload
{
    "user_id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "exp": 1640995200  # expiration timestamp
}
```

**Inter-service Authentication:**
```python
# How other services verify tokens
async def verify_user_token(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://auth-service:8001/verify-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()  # Returns user data
        return None
```

### 2. Order Service (Port 8003)
**Responsibility:** Order management and payment processing

**Database Schema:**
```python
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)  # From Auth Service
    order_number = Column(String, unique=True)  # ORD-2024-001
    status = Column(String, default="pending")  # pending, confirmed, shipped, delivered
    total_amount = Column(Float)
    payment_method = Column(String, default="cash_on_delivery")
    shipping_address = Column(JSON)  # Store address as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer)  # From external API
    product_name = Column(String)
    product_price = Column(Float)
    quantity = Column(Integer)
    subtotal = Column(Float)
```

**API Endpoints:**
- `POST /orders` - Create new order
- `GET /orders/{order_id}` - Get order details
- `GET /users/{user_id}/orders` - Get user's orders
- `PUT /orders/{order_id}/status` - Update order status

**Product Integration:**
```python
# Fetch product details from external API
async def get_product_details(product_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://fakestoreapi.in/api/products/{product_id}")
        return response.json()

# Redis caching for products
async def get_cached_product(product_id: int):
    cached = await redis_client.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from API and cache
    product = await get_product_details(product_id)
    await redis_client.setex(f"product:{product_id}", 3600, json.dumps(product))
    return product
```

### 3. Email Service (Node.js)
**Responsibility:** Send order-related email notifications

**Message Queue Consumer:**
```javascript
// email-service/index.js
const amqp = require('amqplib');
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransporter({
    service: 'gmail',
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

async function consumeOrderEvents() {
    const connection = await amqp.connect('amqp://rabbitmq:5672');
    const channel = await connection.createChannel();
    
    // Order confirmation emails
    await channel.assertQueue('order.created');
    channel.consume('order.created', async (msg) => {
        const orderData = JSON.parse(msg.content.toString());
        
        await transporter.sendMail({
            to: orderData.user_email,
            subject: `Order Confirmation - ${orderData.order_number}`,
            html: generateOrderConfirmationEmail(orderData)
        });
        
        channel.ack(msg);
    });
    
    // Order status update emails
    await channel.assertQueue('order.status_updated');
    channel.consume('order.status_updated', async (msg) => {
        const statusData = JSON.parse(msg.content.toString());
        
        await transporter.sendMail({
            to: statusData.user_email,
            subject: `Order ${statusData.status} - ${statusData.order_number}`,
            html: generateStatusUpdateEmail(statusData)
        });
        
        channel.ack(msg);
    });
}

function generateOrderConfirmationEmail(orderData) {
    return `
        <h2>Order Confirmation</h2>
        <p>Hi ${orderData.user_name},</p>
        <p>Your order ${orderData.order_number} has been confirmed!</p>
        
        <h3>Order Details:</h3>
        <ul>
            ${orderData.items.map(item => `
                <li>${item.product_name} x ${item.quantity} = $${item.subtotal}</li>
            `).join('')}
        </ul>
        
        <p><strong>Total: $${orderData.total_amount}</strong></p>
        <p>Payment Method: ${orderData.payment_method}</p>
        
        <p>We'll notify you when your order ships!</p>
    `;
}
```

## Communication Patterns

### 1. Synchronous Communication (HTTP)
```python
# Order Service → Auth Service (Get user details)
async def get_user_details(user_id: int, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://auth-service:8001/user/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

# Order Service → External Product API
async def validate_products(product_ids: List[int]):
    valid_products = []
    for product_id in product_ids:
        product = await get_cached_product(product_id)
        if product:
            valid_products.append(product)
    return valid_products
```

### 2. Asynchronous Communication (RabbitMQ)
```python
# Order Service publishes events
import aio_pika
import json

async def publish_order_created(order_data: dict):
    connection = await aio_pika.connect_robust("amqp://rabbitmq:5672/")
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

# Usage in order creation
async def create_order(order_request, current_user):
    # Create order in database
    order = Order(**order_data)
    db.add(order)
    db.commit()
    
    # Publish event for email notification
    await publish_order_created({
        "order_number": order.order_number,
        "user_email": current_user.email,
        "user_name": f"{current_user.first_name} {current_user.last_name}",
        "total_amount": order.total_amount,
        "items": order_items_data,
        "payment_method": order.payment_method
    })
    
    return order
```

## Redis Implementation

### Caching Strategy:
```python
import redis
import json

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Cache product details (1 hour)
async def cache_product(product_id: int, product_data: dict):
    await redis_client.setex(
        f"product:{product_id}",
        3600,
        json.dumps(product_data)
    )

# Cache user session data (24 hours)
async def cache_user_session(user_id: int, user_data: dict):
    await redis_client.setex(
        f"user_session:{user_id}",
        86400,
        json.dumps(user_data)
    )

# Rate limiting for order creation
async def check_order_rate_limit(user_id: int) -> bool:
    key = f"order_limit:{user_id}"
    current = await redis_client.get(key)
    
    if current is None:
        await redis_client.setex(key, 300, 1)  # 1 order per 5 minutes
        return True
    elif int(current) < 3:  # Max 3 orders per 5 minutes
        await redis_client.incr(key)
        return True
    return False
```

## Project Structure
```
ecommerce-microservices/
├── auth-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   ├── utils/
│   │   │   ├── jwt_handler.py
│   │   │   └── password.py
│   │   └── database.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── order-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   └── orders.py
│   │   ├── services/
│   │   │   ├── product_service.py
│   │   │   ├── auth_service.py
│   │   │   └── message_publisher.py
│   │   └── database.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── email-service/
│   ├── index.js
│   ├── package.json
│   ├── Dockerfile
│   └── templates/
│       ├── order-confirmation.html
│       └── status-update.html
├── docker-compose.yml
├── nginx.conf
├── .env.global
└── README.md
```

## Docker Configuration

### docker-compose.yml:
```yaml
version: '3.8'

services:
  # Microservices
  auth-service:
    build: ./auth-service
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@auth-db:5432/auth_db
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - auth-db
      - redis

  order-service:
    build: ./order-service
    ports:
      - "8003:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@order-db:5432/order_db
      - REDIS_URL=redis://redis:6379
      - RABBITMQ_URL=amqp://rabbitmq:5672/
      - AUTH_SERVICE_URL=http://auth-service:8000
    depends_on:
      - order-db
      - redis
      - rabbitmq

  email-service:
    build: ./email-service
    environment:
      - RABBITMQ_URL=amqp://rabbitmq:5672/
      - EMAIL_USER=${EMAIL_USER}
      - EMAIL_PASS=${EMAIL_PASS}
    depends_on:
      - rabbitmq

  # Databases
  auth-db:
    image: postgres:13
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - auth_db_data:/var/lib/postgresql/data

  order-db:
    image: postgres:13
    environment:
      POSTGRES_DB: order_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - order_db_data:/var/lib/postgresql/data

  # Infrastructure
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=admin

  # API Gateway (Optional)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - auth-service
      - order-service

volumes:
  auth_db_data:
  order_db_data:
```

## API Flow Examples

### 1. User Registration & Login:
```
POST /auth-service/register
{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "secure123"
}

POST /auth-service/login
{
    "username": "john_doe",
    "password": "secure123"
}
Response: {"access_token": "jwt_token_here"}
```

### 2. Create Order Flow:
```
1. Client: POST /order-service/orders
   Headers: Authorization: Bearer jwt_token
   Body: {
       "items": [
           {"product_id": 1, "quantity": 2},
           {"product_id": 5, "quantity": 1}
       ],
       "shipping_address_id": 1
   }

2. Order Service → Auth Service: Verify user token
3. Order Service → External API: Fetch product details
4. Order Service → Redis: Cache product data
5. Order Service → Database: Save order
6. Order Service → RabbitMQ: Publish order.created event
7. Email Service ← RabbitMQ: Consume event & send email
```

## Development Timeline (7 days):

**Day 1:** Project setup, Docker compose, databases
**Day 2:** Auth Service (JWT, user management, addresses)
**Day 3:** Order Service (order creation, product integration)
**Day 4:** Redis caching, rate limiting
**Day 5:** RabbitMQ setup, message publishing
**Day 6:** Email Service (Node.js, email templates)
**Day 7:** Testing, deployment, documentation

## Key Learning Outcomes:
- **Microservices**: Independent services with clear boundaries
- **JWT Authentication**: Token-based auth across services
- **External API Integration**: Working with third-party APIs
- **Caching Strategy**: Redis for performance optimization
- **Message Queue**: Asynchronous communication with RabbitMQ
- **Email Automation**: Event-driven notifications
- **Docker**: Multi-service containerization
- **Database Per Service**: Microservices data independence

This architecture demonstrates production-ready patterns while being focused and achievable in one week!