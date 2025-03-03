from datetime import datetime
from supabase import create_client
from FixBot.FixBot.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_matched_questions_with_all_data():
    response = supabase.table('matched_questions_tmp').select(
        "refined_question", "matched_transcript", "pko_t5_answer", "final_answer", "reference_urls", "embedding"
    ).execute()
    return response.data

def save_to_video_qa(item):
    record = {
        'question': item['refined_question'],
        'matched_transcript': item['matched_transcript'],
        'initial_answer': item['pko_t5_answer'],
        'final_answer': item['final_answer'],
        'video_url': item['reference_urls'][0] if item['reference_urls'] else None,
        'embedding': item['embedding'],
        'reference_urls': item['reference_urls'],
        'created_at': datetime.now().isoformat()
    }

    supabase.table('video_qa').insert(record).execute()
    print(f"✅ Saved to video_qa: {item['refined_question']}")
