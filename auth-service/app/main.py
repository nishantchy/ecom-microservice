from fastapi import FastAPI
from app.configs.config import settings
from app.configs.database import create_db_and_tables
from app.routes import users, auth, verify

create_db_and_tables()

app = FastAPI()

print(settings.DATABASE_URL)
print(settings.JWT_SECRET)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(verify.router)

@app.get("/")
async def root():
    return "Server running at http://localhost:8000"

