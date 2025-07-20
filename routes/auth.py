from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from core.supabase import signup_user, login_user, supabase
from datetime import datetime, timedelta, timezone

ACCESS_TOKEN_EXPIRE_MINUTES = 60  

router = APIRouter()

@router.post("/signup")
async def signup(request: Request):
    body = await request.json()
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    res = signup_user(email, password)
    if res.status_code == 200:
        user_id = res.json()["user"]["id"]
        supabase.table("users").insert({"id": user_id, "email": email, "role": "user"}).execute()
        return {"message": "Signup successful"}
    raise HTTPException(status_code=400, detail=res.text)

@router.post("/login")
async def login(request: Request):
    body = await request.json()
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    res = login_user(email, password)
    if res.status_code == 200:
        tokens = res.json()
        response = JSONResponse(content={"message": "Login successful"})
        expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            expires=expires
        )
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True
        )
        return response

    raise HTTPException(status_code=400, detail=res.text)
