from fastapi import FastAPI
from app.configs.config import settings
from app.configs.database import create_db_and_tables
from app.routes import order


create_db_and_tables()

app = FastAPI()

print(settings.DATABASE_URL)
print(settings.PRODUCTS_API)

app.include_router(order.router)

@app.get("/")
async def root():
    return "Server running at http://localhost:8001"


# To run this service on port 8001, use:
# uvicorn app.main:app --reload --port 8001

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

