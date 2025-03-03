import os
import time
import json
from groq import Groq
from supabase import create_client, Client
from FixBot.FixBot.config import SUPABASE_URL, SUPABASE_KEY, GROQ_API_KEY

# ======== 환경 설정 ========
MODEL_NAME = "llama3-8b-8192"

# ======== Supabase & Groq 초기화 ========
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# ======== 질문 생성 클래스 ========
class QuestionGenerator:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate_questions(self, sentences):
        document_text = "\n".join([f"{i+1}. {sent}" for i, sent in enumerate(sentences)])

        prompt = f"""
        ## 역할
        너는 세탁기 전문가 AI야.
        아래는 세탁기 관련 정보 문장들이다.
        각 문장을 보고, 사용자들이 실제 궁금해할 법한 "실용적인" 질문을 생성해줘.
        광고성 문구, 브랜드명, 의미 없는 문장은 무시하고, 꼭 필요한 정보에서만 질문을 생성해.

        ## 생성 조건
        - 각 문장 당 1~2개 이상의 "실제 궁금할 법한 질문" 생성
        - 너무 단순하거나 쓸모없는 질문 금지
        - 문장과 무관한 질문 금지
        - 한국어로만 출력 (영어 금지)
        - 각 질문은 한 줄로 출력
        - 아래 예시 참고

        ## 예시
        문장: "세탁기 필터는 2주마다 세척해야 합니다."
        질문: "세탁기 필터 청소는 얼마나 자주 해야 하나요?"
        질문: "세탁기 필터 청소 방법은?"

        문장: "세탁기에서 쉿내가 날 때 대처법"
        질문: "세탁기에서 쉿내가 나는 원인은 무엇인가요?"
        질문: "세탁기 쉿내 제거 방법은?"

        ## 입력 문장 목록
        {document_text}

        ## 출력 규칙
        - 질문만 출력 (각 줄에 1개씩 출력)
        - 설명, 문장 번호 등 출력 금지
        - 최대 2개까지 생성
        """

        response = groq_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        raw_questions = response.choices[0].message.content.strip().split("\n")
        cleaned_questions = self.clean_generated_questions(raw_questions)
        return [q.strip() for q in cleaned_questions if q.strip()]

    @staticmethod
    def clean_generated_questions(raw_response_lines):
        filtered_questions = []
        for line in raw_response_lines:
            if line.strip().lower().startswith("here are"):
                continue
            filtered_questions.append(line.strip())
        return filtered_questions

# ======== 질문 정제 클래스 ========
class QuestionRefiner:
    def refine(self, question):

        prompt = f"""
        ## 역할
        너는 한국어 질문 정제 전문가야.
        아래 사용자 질문을 보고, 의미는 유지하면서 더 자연스럽고 명확하게 정제해줘.

        ## 정제 조건
        - 문장 의미는 유지
        - 사용자 입장에서 이해하기 쉽게
        - 너무 전문적이거나 어려운 단어 사용 금지
        - 불필요한 표현, 광고성 문구 제거
        - 질문 하나만 출력
        - 한 줄로만 출력 (줄바꿈 금지)

        ## 예시
        입력: "세탁기에서 쉿내가 날 때 어떻게 하나요?"
        출력: "세탁기에서 쉿내가 날 때 해결 방법은?"

        입력: "LG 드럼세탁기에서 E3 에러 고치는 방법"
        출력: "LG 드럼세탁기 E3 오류 해결 방법은?"

        ## 입력된 질문
        {question}

        ## 출력
        """

        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=100
        )

        refined_question = response.choices[0].message.content.strip()

        return refined_question

# ======== Supabase 업로드 클래스 ========
class SupabaseUploader:
    def upload(self, original_question, refined_question, original_sentence, source):
        data = {
            "original_question": original_question,
            "refined_question": refined_question,
            "original_sentence": original_sentence,
            "source": source
        }
        supabase.table("question_embeddings").insert(data).execute()

# ======== 메인 실행 함수 ========
def main():
    # 파일 로드
    with open("/content/drive/MyDrive/FixBot/cleaned_sentences_saved.json", "r", encoding="utf-8") as f:
        sentences_data = json.load(f)

    generator = QuestionGenerator(MODEL_NAME)
    refiner = QuestionRefiner()
    uploader = SupabaseUploader()

    batch_size = 15
    batches = [sentences_data[i:i+batch_size] for i in range(0, len(sentences_data), batch_size)]

    for batch_idx, batch in enumerate(batches):
        print(f"🔹 {batch_idx+1}/{len(batches)}번째 배치 처리 중...")

        sentences = [item["sentence"] for item in batch]
        questions = generator.generate_questions(sentences)

        for i, (sentence_item, question) in enumerate(zip(batch, questions)):
            original_sentence = sentence_item["sentence"]
            source = sentence_item["url"]

            refined_question = refiner.refine(question)

            print(f"✅ [{batch_idx+1}-{i+1}] 원문장: {original_sentence}")
            print(f"➡ 생성질문: {question}")
            print(f"➡ 정제질문: {refined_question}")
            print(f"🌐 출처: {source}")
            print("-" * 60)

            uploader.upload(question, refined_question, original_sentence, source)

            time.sleep(1)  # Rate limit 보호

if __name__ == "__main__":
    main()