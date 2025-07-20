from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import SUPABASE_URL, SUPABASE_KEY
import httpx

security = HTTPBearer(auto_error=False)

async def verify_request_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token missing")
    return await verify_token_direct(token)

async def verify_token_direct(token: str):
    url = f"{SUPABASE_URL}/auth/v1/user"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {token}"
            })
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token verification failed: {str(e)}")