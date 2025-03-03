# FixBot 폴더를 sys.path에 추가
from FixBot.config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
from datetime import datetime

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_video_questions():
    return supabase.table('video_questions').select("question, transcript, embedding, video_url").execute().data

def fetch_samsung_qna():
    return supabase.table('samsung_qna').select("question, answer, embedding").execute().data

def save_to_tmp_table(question, transcript, answer, embedding, video_url):
    record = {
        "refined_question": question,
        "transcript": transcript,
        "answer": answer,
        "embedding": embedding,
        "video_url": video_url,
        "created_at": datetime.now().isoformat()
    }
    supabase.table('questions_tmp').insert(record).execute()
