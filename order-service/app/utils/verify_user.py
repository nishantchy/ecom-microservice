import httpx
from app.configs.config import settings

async def verify_user_token(token: str):
    url = f"{settings.AUTH_SERVICE}/api/verify-token/"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"token": token}
        )
        if response.status_code == 200:
            return response.json()
        return None 