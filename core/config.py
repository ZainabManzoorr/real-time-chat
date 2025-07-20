import os
from dotenv import load_dotenv

load_dotenv()



SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


headers = {
  "apikey": SUPABASE_KEY,
  "Authorization": f"Bearer {SUPABASE_KEY}",
  "Content-Type": "application/json"
}

