from .question_filter import is_valid_question
from .question_repository import fetch_video_questions, fetch_samsung_qna, save_to_tmp_table

def run_step1():
    video_questions = fetch_video_questions()
    samsung_qna = fetch_samsung_qna()

    total_count, saved_count = 0, 0

    for item in video_questions + samsung_qna:
        total_count += 1
        question = item['question']
        if is_valid_question(question):
            save_to_tmp_table(
                question=question,
                transcript=item.get('transcript'),
                answer=item.get('answer'),
                embedding=item['embedding'],
                video_url=item.get('video_url')
            )
            saved_count += 1

    print(f"✅ [Step 1] Total: {total_count}, Saved: {saved_count}")
