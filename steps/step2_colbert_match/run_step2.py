from .colbert_matcher import get_top_segments, split_into_sentences, fetch_similar_questions
from .question_repository import fetch_all_records, save_matched_result
import numpy as np
from supabase import create_client
from FixBot.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_step2():
    questions = supabase.table('questions_tmp').select("refined_question", "embedding").execute().data

    video_questions = fetch_all_records("video_questions", ["question", "transcript", "video_url", "embedding"])
    samsung_questions = fetch_all_records("samsung_qna", ["question", "answer", "embedding"])

    for question in questions:
        refined_question, embedding = question['refined_question'], np.array(question['embedding'])

        matches = fetch_similar_questions(embedding, video_questions + samsung_questions, top_k=3)

        combined_transcript, combined_urls = [], []
        for match in matches:
            if 'transcript' in match:
                combined_transcript.extend(get_top_segments(embedding, split_into_sentences(match['transcript'])))
                if match.get('video_url'):
                    combined_urls.append(match['video_url'])
            if 'answer' in match:
                combined_transcript.append(match['answer'])

        save_matched_result(refined_question, embedding.tolist(), "\n".join(combined_transcript), combined_urls)

    print("✅ [Step 2] Matching complete.")
