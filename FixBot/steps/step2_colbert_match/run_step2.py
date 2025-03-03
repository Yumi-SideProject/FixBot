import json
from supabase import create_client
from FixBot.config import SUPABASE_URL, SUPABASE_KEY
from steps.step2_colbert_match.KoSimCSE import get_top_segments, split_into_sentences, fetch_similar_questions, get_embedding
from steps.step2_colbert_match.question_repository import fetch_all_records, save_matched_result

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_embedding_if_needed(record):
    if isinstance(record['embedding'], str):
        try:
            record['embedding'] = json.loads(record['embedding'])
        except json.JSONDecodeError:
            raise ValueError(f"Invalid embedding format: {record['embedding']}")

def run_step2():
    questions = supabase.table('questions_tmp').select("refined_question").execute().data

    video_questions = fetch_all_records("video_questions", ["question", "transcript", "video_url", "embedding"])
    samsung_questions = fetch_all_records("samsung_qna", ["question", "answer", "embedding"])

    for record in video_questions + samsung_questions:
        parse_embedding_if_needed(record)

    for question in questions:
        refined_question = question['refined_question']
        embedding = get_embedding(refined_question)

        # 유사한 자막/QnA 찾기
        matches = fetch_similar_questions(embedding, video_questions + samsung_questions, top_k=3, threshold=0.7)

        # 임계치 넘는 자막이 없을 경우
        if not matches:
            combined_transcript = ["관련된 참고 자료를 찾지 못했습니다."]
            combined_urls = []
        else:
            combined_transcript = []
            combined_urls = []

            for match in matches:
                if 'transcript' in match:
                    combined_transcript.extend(get_top_segments(embedding, split_into_sentences(match['transcript'])))
                    if match.get('video_url'):
                        combined_urls.append(match['video_url'])
                if 'answer' in match:
                    combined_transcript.append(match['answer'])

        # 최종 저장
        save_matched_result(
            refined_question,
            embedding.tolist(),
            "\n".join(combined_transcript),
            combined_urls
        )

    print("✅ [Step 2] Matching complete.")