from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.room import router as room_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(room_router, prefix="/room")
app.include_router(chat_router, prefix="/chat")
