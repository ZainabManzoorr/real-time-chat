from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.dependencies import verify_token_direct
from core.ws_manager import ConnectionManager
from core.supabase import supabase

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/chat/{room_id}")
async def chat_ws(websocket: WebSocket, room_id: str, token: str = Query(None)):
    if not token:
        await websocket.close(code=1008)
        return

    try:
        user = await verify_token_direct(token)
        if user.get("role") != "user":
            await websocket.close(code=1008)
            return
    except:
        await websocket.close(code=1008)
        return

    await manager.connect(room_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(room_id, message)
            supabase.table("messages").insert({
                "room_id": room_id,
                "sender_id": user["sub"],
                "content": message
            }).execute()
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)