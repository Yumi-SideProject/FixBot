import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase 환경변수가 제대로 설정되지 않았습니다.")
