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

    # Check for existing room with either user combination
    # Get user ID from the user object (try different possible keys)
    current_user_id = user.get('id') or user.get('sub') or user.get('user_id')
    
    # Debug: Print the user object to see its structure
    print(f"User object: {user}")
    print(f"Extracted current_user_id: {current_user_id}")
    print(f"Provided other_user_id: {other_user_id}")
    
    if not current_user_id:
        raise HTTPException(status_code=400, detail="Could not determine user ID")

    
    
    # Prevent creating a room with yourself
    if current_user_id == other_user_id:
        raise HTTPException(status_code=400, detail="Cannot create a chat room with yourself")
    
    try:
        print("Checking for existing room...")
        
        # First, check if a room already exists between these users
        # Try first combination: user1_id = current_user, user2_id = other_user
        existing1 = supabase.table("chat_rooms").select("*").eq("user1_id", current_user_id).eq("user2_id", other_user_id).maybe_single().execute()
        print(f"First query result: {existing1}")
        
        # If first query found a room, return it immediately
        if existing1.data:
            print(f"Found existing room in first query: {existing1.data}")
            return {"room_id": existing1.data["id"]}
        
        # Only try second query if first query didn't find anything
        existing2 = supabase.table("chat_rooms").select("*").eq("user1_id", other_user_id).eq("user2_id", current_user_id).maybe_single().execute()
        print(f"Second query result: {existing2}")
        
        # Check if second query found an existing room
        if existing2.data:
            print(f"Found existing room in second query: {existing2.data}")
            return {"room_id": existing2.data["id"]}
        
        # If no existing room, create a new one
        print("Creating new room...")
        room_id = str(uuid4())
        print(f"Generated room_id: {room_id}")
        
        result = supabase.table("chat_rooms").insert({
            "id": room_id,
            "user1_id": current_user_id,
            "user2_id": other_user_id
        }).execute()
        
        print(f"Insert result: {result}")
        return {"room_id": room_id}
        
    except Exception as e:
        print(f"Error in room creation: {str(e)}")
        print(f"Current user ID: {current_user_id}")
        print(f"Other user ID: {other_user_id}")
        raise HTTPException(status_code=500, detail=f"Room creation failed: {str(e)}")

    return {"room_id": room_id}


