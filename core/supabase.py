from supabase import create_client, Client
from core.config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

import httpx

def signup_user(email, password, role="user"):
    url = f"{SUPABASE_URL}/auth/v1/signup"
    data = {
        "email": email,
        "password": password,
        "data": {"role": role}
    }
    return httpx.post(url, json=data, headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"})

def login_user(email, password):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    data = {"email": email, "password": password}
    return httpx.post(url, json=data, headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"})