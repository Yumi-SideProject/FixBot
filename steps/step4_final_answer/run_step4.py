from .final_answer_generator import generate_final_answer
from .question_repository import fetch_matched_questions_with_t5, save_final_answer

def run_step4():
    matched_data = fetch_matched_questions_with_t5()

    for item in matched_data:
        final_answer = generate_final_answer(
            item['refined_question'],
            item['pko_t5_answer'],
            item['matched_transcript']
        )

        save_final_answer(item['id'], final_answer)
        print(f"✅ Final Answer Generated for: {item['refined_question']}")

    print(f"✅ All final answers saved to matched_questions_tmp.")
