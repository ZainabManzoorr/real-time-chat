from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.dependencies import verify_token_direct
from core.ws_manager import ConnectionManager
from core.supabase import supabase

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/chat/{room_id}")
async def chat_ws(websocket: WebSocket, room_id: str, token: str = Query(None)):
    print(f"WebSocket connection attempt for room: {room_id}")
    
    if not token:
        print("No token provided, closing connection")
        await websocket.close(code=1008)
        return

    try:
        user = await verify_token_direct(token)
        print(f"User authenticated: {user.get('email')}")
        
        # Check role in user_metadata instead of top-level role
        user_role = user.get("user_metadata", {}).get("role")
        print(f"User role: {user_role}")
        
        if user_role != "user":
            print(f"Invalid role: {user_role}, closing connection")
            await websocket.close(code=1008)
            return
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        await websocket.close(code=1008)
        return

    print(f"Connecting user to room: {room_id}")
    await manager.connect(room_id, websocket)
    print(f"User connected to room: {room_id}")

    try:
        while True:
            message = await websocket.receive_text()
            print(f"Received message: {message}")
            
            # Handle ping messages
            if message == "ping":
                await websocket.send_text("pong")
                print("Sent pong response")
                continue
            
            # Broadcast the message to all users in the room
            await manager.broadcast(room_id, message)
            
            # Store message in database
            supabase.table("messages").insert({
                "chat_room_id": room_id,
                "sender_id": user.get("id") or user.get("sub") or user.get("user_id"),
                "content": message,
                "message_type": "text",
                "is_read": False
            }).execute()
            print(f"Message stored in database")
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for room: {room_id}")
        manager.disconnect(room_id, websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(room_id, websocket)