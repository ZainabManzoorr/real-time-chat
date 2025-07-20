from fastapi import APIRouter, Request, Depends, HTTPException
from core.dependencies import verify_request_token
from core.supabase import supabase
from uuid import uuid4

router = APIRouter()

@router.post("/get_or_create")
async def get_or_create_room(request: Request, user=Depends(verify_request_token)):
    body = await request.json()
    other_user_id = body.get("other_user_id")

    if not other_user_id:
        raise HTTPException(status_code=400, detail="Missing other user ID")

    existing = supabase.table("chat_rooms").select("*").or_(
        f"(user1.eq.{user['sub']},user2.eq.{other_user_id})",
        f"(user1.eq.{other_user_id},user2.eq.{user['sub']})"
    ).maybe_single().execute()

    if existing.data:
        return {"room_id": existing.data["id"]}

    room_id = str(uuid4())
    supabase.table("chat_rooms").insert({
        "id": room_id,
        "user1": user["sub"],
        "user2": other_user_id
    }).execute()

    return {"room_id": room_id}

