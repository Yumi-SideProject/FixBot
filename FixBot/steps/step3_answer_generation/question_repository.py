from supabase import create_client
from FixBot.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_matched_questions():
    response = supabase.table('matched_questions_tmp').select("id", "refined_question", "matched_transcript").execute()
    return response.data

def save_t5_answer(question_id, t5_answer):
    supabase.table('matched_questions_tmp').update({"pko_t5_answer": t5_answer}).eq("id", question_id).execute()
