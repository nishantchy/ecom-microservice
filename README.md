# E-commerce Order Management - Microservices Architecture

## System Overview

This project is a microservices-based e-commerce order management system, inspired by Amazon's architecture. It demonstrates:

- User authentication and management
- Order creation and management
- Email notifications for order events
- Integration with an external product API (fakestoreapi.in)
- Asynchronous communication using RabbitMQ
- Caching and rate limiting with Redis
- Polyglot persistence (PostgreSQL, MongoDB)
- Containerization with Docker

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend/     │    │   Auth Service  │    │  Order Service  │
│   Mobile App    │◄──►│    (Port 8000)  │◄──►│   (Port 8001)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│External Product │    │     Redis       │    │    RabbitMQ     │
│API (fakestore)  │    │   (Rate Limit)  │    │ (Message Queue) │
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

---

## Microservices Breakdown

### 1. Auth Service (FastAPI, PostgreSQL)

- **Port:** 8000
- **Responsibilities:**
  - User registration, login, JWT token generation
  - Token verification for other services
  - User profile and address management
- **Key Endpoints:**
  - `POST /register` — Register a new user
  - `POST /login` — User login, returns JWT
  - `POST /verify-token` — Verify JWT (used by other services)
  - `GET /user/{user_id}` — Get user details
- **Database:** PostgreSQL

### 2. Order Service (FastAPI, PostgreSQL, Redis, RabbitMQ)

- **Port:** 8003
- **Responsibilities:**
  - Order creation and management
  - Fetch product details from external API
  - Rate limiting (Redis)
  - Publishes order events to RabbitMQ
- **Key Endpoints:**
  - `POST /api/orders/` — Create a new order (rate-limited)
  - `GET /api/orders/{order_id}` — Get order details
  - `GET /api/orders/` — List all orders
- **Database:** PostgreSQL
- **Caching/Rate Limiting:** Redis
- **Async Messaging:** Publishes to RabbitMQ (`order.created` queue)

### 3. Email Service (Node.js, MongoDB, RabbitMQ)

- **Responsibilities:**
  - Consumes `order.created` events from RabbitMQ
  - Sends order confirmation emails using Nodemailer (Gmail)
  - Logs sent emails to MongoDB
- **No public HTTP endpoints required for core functionality**
- **Database:** MongoDB (Atlas or compatible)
- **Async Messaging:** Consumes from RabbitMQ (`order.created` queue)

---

## Communication Patterns

### Synchronous (HTTP)

- **Order Service → Auth Service:** Verifies JWT token and fetches user info
- **Order Service → External Product API:** Fetches product details

### Asynchronous (RabbitMQ)

- **Order Service → Email Service:** Publishes `order.created` event
- **Email Service:** Consumes event, sends email, logs to MongoDB

---

## Environment Variables

Each service uses its own `.env` file. Example variables:

### Auth Service

```
DATABASE_URL=""
JWT_SECRET=your_jwt_secret
REDIS_URL=redis://host:6379
```

### Order Service

```
DATABASE_URL=""
PRODUCTS_API=https://fakestoreapi.in/api/products
AUTH_SERVICE=http://auth-service:8001
RABBITMQ_URL=""
REDIS_URL=redis://host:6379
```

### Email Service

```
RABBITMQ_URL=""
MONGODB_URI=""
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
```

---

## Setup & Running Locally

1. **Clone the repository**
2. **Set up environment variables** for each service
3. **Start infrastructure** (PostgreSQL, Redis, RabbitMQ, MongoDB) — use Docker Compose or cloud services
4. **Start each service:**
   - Auth Service: `uvicorn app.main:app --reload --port 8000`
   - Order Service: `uvicorn app.main:app --reload --port 8001`
   - Email Service: `npm run build && node dist/index.js` (after setting up Node.js and dependencies)
5. **Access API docs:**
   - Auth Service: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Order Service: [http://localhost:8001/docs](http://localhost:8001/docs)

---

## Deployment Notes

- Each service can be containerized and deployed independently.
- Use Docker Compose for local orchestration; for production, deploy each service separately (e.g., Render, AWS, GCP).
- Use managed services for PostgreSQL, MongoDB, Redis, and RabbitMQ in production.
- Use an API Gateway (e.g., Nginx) for a single entry point if desired.

---

## Key Features & Learnings

- **Microservices:** Each service is independent and can be scaled or deployed separately.
- **JWT Authentication:** Secure, stateless user authentication across services.
- **External API Integration:** Product data fetched from fakestoreapi.in.
- **Caching & Rate Limiting:** Redis used for performance and abuse prevention.
- **Async Messaging:** RabbitMQ enables decoupled, reliable event-driven communication.
- **Email Automation:** Nodemailer + Gmail for transactional emails.
- **Polyglot Persistence:** PostgreSQL for structured data, MongoDB for flexible email logs.
- **Dockerized:** All services can be run in containers for easy development and deployment.

---

## Project Structure

```
ecommerce/
├── auth-service/
├── order-service/
├── email-service/
├── docker-compose.yml
├── nginx.conf (optional)
└── README.md
```

---

## Example Order Event Payload (RabbitMQ)

```json
{
  "order_number": 12345,
  "user_email": "user@example.com",
  "user_name": "John Doe",
  "total_amount": 100,
  "items": [{ "product_id": 1, "quantity": 2, "price": 50, "total_amt": 100 }],
  "payment_method": "cash_on_delivery"
}
```

---

## Development Timeline (Sample)

- **Day 1:** Project setup, Docker Compose, databases
- **Day 2:** Auth Service (JWT, user management)
- **Day 3:** Order Service (order creation, product integration)
- **Day 4:** Redis caching, rate limiting
- **Day 5:** RabbitMQ setup, message publishing
- **Day 6:** Email Service (Node.js, email templates)
- **Day 7:** Testing, deployment, documentation

---

## Credits

- [fakestoreapi.in](https://fakestoreapi.in) for product data
- [CloudAMQP](https://www.cloudamqp.com/) for free RabbitMQ
- [Supabase](https://supabase.com/) for free PostgreSQL Databases
- [MongoDB Atlas](https://www.mongodb.com/atlas/database) for free MongoDB
- [Redis Cloud](https://redis.com/try-free/) for free Redis

---

This architecture demonstrates production-ready microservices patterns, event-driven communication, and modern cloud-native best practices.
dsf
