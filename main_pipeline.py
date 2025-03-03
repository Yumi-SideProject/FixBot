from steps.step1_question_filter.run_step1 import run_step1
from steps.step2_colbert_match.run_step2 import run_step2
from steps.step3_answer_generation.run_step3 import run_step3
from steps.step4_final_answer.run_step4 import run_step4
from steps.step5_save_to_db.run_step5 import run_step5

def main():
    print("🔹 Step 1: 질문 필터링 시작")
    run_step1()

    print("🔹 Step 2: 유사도 매칭 시작")
    run_step2()

    print("🔹 Step 3: T5 보완 답변 생성 시작")
    run_step3()

    print("🔹 Step 4: GPT-4 최종 답변 생성 시작")
    run_step4()

    print("🔹 Step 5: 최종 결과 video_qa 저장 시작")
    run_step5()

    print("✅ 전체 파이프라인 완료")

if __name__ == "__main__":
    main()
