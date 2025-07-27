from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from core.supabase import signup_user, login_user, supabase
from datetime import datetime, timedelta, timezone
from core.dependencies import verify_request_token

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
        # Extract username from email (everything before @)
        username = email.split('@')[0]
        supabase.table("users").insert({
            "id": user_id, 
            "email": email, 
            "username": username,
            "role": "user",
            "preferences": {}  # Initialize empty JSON object
            # Other columns will use their default values:
            # created_at: now()
            # updated_at: now()
            # body_type: NULL
            # skin_tone: NULL
            # latitude: NULL
            # longitude: NULL
        }).execute()
        return {"message": "Signup successful"}
    raise HTTPException(status_code=400, detail=res.text)

@router.get("/user")
async def get_user(user=Depends(verify_request_token)):
    """Get current user information"""
    return user
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
        user_id = tokens.get("user", {}).get("id")
        
        response = JSONResponse(content={
            "message": "Login successful",
            "user_id": user_id
        })
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
