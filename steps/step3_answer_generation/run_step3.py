from .t5_answer_generator import generate_t5_answer
from .question_repository import fetch_matched_questions, save_t5_answer

def run_step3():
    matched_data = fetch_matched_questions()

    for item in matched_data:
        t5_answer = generate_t5_answer(item['refined_question'], item['matched_transcript'])
        save_t5_answer(item['id'], t5_answer)
        print(f"✅ T5 Answer Generated for: {item['refined_question']}")

    print(f"✅ All T5 answers saved to matched_questions_tmp.")
