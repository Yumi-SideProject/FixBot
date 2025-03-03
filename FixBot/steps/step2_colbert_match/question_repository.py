from FixBot.config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
from datetime import datetime

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_all_records(table_name, columns):
    return supabase.table(table_name).select(",".join(columns)).execute().data

def save_matched_result(refined_question, embedding, matched_transcript, reference_urls):
    record = {
        "refined_question": refined_question,
        "embedding": embedding,
        "matched_transcript": matched_transcript,
        "reference_urls": reference_urls,
        "created_at": datetime.now().isoformat()
    }
    supabase.table('matched_questions_tmp').insert(record).execute()
