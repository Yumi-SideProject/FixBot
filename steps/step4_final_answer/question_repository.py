from supabase import create_client
from FixBot.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_matched_questions_with_t5():
    response = supabase.table('matched_questions_tmp').select(
        "id", "refined_question", "matched_transcript", "pko_t5_answer"
    ).execute()
    return response.data

def save_final_answer(question_id, final_answer):
    supabase.table('matched_questions_tmp').update(
        {"final_answer": final_answer}
    ).eq("id", question_id).execute()
