import json
import time
from groq import Groq  # 🔥 Groq API 사용

# ✅ Groq API 설정
API_KEY = "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"  # 🔥 여기에 Groq API Key 입력
client = Groq(api_key=API_KEY)  # 🔥 API Key를 사용하여 Groq 클라이언트 초기화

# 📌 LLM 모델 정보
MODEL_NAME = "llama3-70b-8192"

# 📌 파일 경로
input_path = "/content/drive/MyDrive/FixBot/cleaned_sentences.json"
output_path = "/content/drive/MyDrive/FixBot/generated_questions_llm.txt"

# 📌 JSON 파일 로드
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 📌 문장 리스트 생성
sentences = [item["sentence"] for item in data]

# 📌 문장을 15개씩 그룹화
batch_size = 15
sentence_batches = [sentences[i : i + batch_size] for i in range(0, len(sentences), batch_size)]

# 📌 LLM을 이용한 질문 생성
def generate_questions(sentence_batches):
    """LLM을 사용해 한 번에 15개의 문장으로 질문 생성"""
    # relevant_sentences가 비어 있을 경우 대비
    if not sentence_batches:
        document_text = "세탁기 사용법 및 문제 해결과 관련된 문장들이 제공될 예정입니다. 이 문장을 바탕으로 질문을 생성해주세요."
    else:
        document_text = "\n".join([f"{i+1}. {sent}" for i, sent in enumerate(sentence_batches)])

    # 🔥 LLM 프롬프트
    prompt = f"""
   ## 너의 역할:
- 너는 **세탁기 관련 GPT 모델을 학습시키기 위한 질문 생성 AI**야.
- 제공된 문서를 바탕으로, 사용자가 세탁기 관련하여 자주 묻는 질문을 예측하여 생성해야 해.

## 문서 설명:
- 제공된 문서는 **세탁기 및 건조기 사용법, 유지보수, 문제 해결 방법**이 포함된 유튜브 영상의 자막 데이터야.
- 문서에는 다양한 세탁기 관련 정보가 포함되어 있으며, 이 정보를 활용하여 실용적인 질문을 만들어야 해.

## 질문 생성 규칙:
1. **각 문장에 대해 사용자가 실제로 궁금해할 만한 "세탁 주제의" 질문을 생성해야 해.**
2. **질문은 명확하고 구체적이어야 해.**
3. **질문의 유형을 다양하게 구성해야 해.**
   - "어떻게", "왜", "언제", "무엇을", "어떤", "차이점" 등을 활용하여 자연스럽게 질문을 만들 것.
   - 단순한 사실 확인 질문이 아닌, 문제 해결과 연관된 질문을 포함할 것.
4. **너무 일반적인 질문은 피하고, 문서의 내용을 반영한 세부적인 질문을 생성해야 해.**
5. **실제 소비자가 세탁기 사용 중에 겪을 수 있는 문제나 궁금증을 반영한 질문을 우선 생성할 것.**

## 예시 (입력 문장 → 생성된 질문):
- 입력 문장: "건조기를 사용할 때 필터 청소를 꼭 해야 합니다."
  - 생성된 질문: "건조기 필터 청소는 얼마나 자주 해야 하나요?"
  - 생성된 질문: "건조기 필터를 청소하지 않으면 어떤 문제가 발생할 수 있나요?"

- 입력 문장: "세탁기의 배수 필터를 정기적으로 청소해야 합니다."
  - 생성된 질문: "세탁기 배수 필터 청소는 어떻게 하나요?"
  - 생성된 질문: "배수 필터가 막히면 어떤 증상이 나타날까요?"

- 입력 문장: "드럼 세탁기와 일반 세탁기의 차이점은 무엇일까요?"
  - 생성된 질문: "드럼 세탁기와 일반 세탁기는 어떤 차이가 있나요?"
  - 생성된 질문: "드럼 세탁기의 장점과 단점은 무엇인가요?"

## 문서:
{document_text}

## 출력 형식:
- 생성된 질문을 한 줄씩 출력해야 해.
- 불필요한 설명 없이 **질문만** 작성할 것.

## 질문 목록:
    """

    # 🔥 LLM API 호출
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=400,
        top_p=0.9,
        stream=False
    )

    generated_text = response.choices[0].message.content.strip()
    generated_questions = generated_text.split("\n")  # 줄바꿈 기준으로 질문 분할

    return [q.strip() for q in generated_questions if q.strip()]

# ✅ LLM을 사용해 질문 생성
all_questions = []
for idx, batch in enumerate(sentence_batches):
    print(f"📝 {idx+1}/{len(sentence_batches)} 번째 배치 질문 생성 중...")

    questions = generate_questions(batch)
    print(questions)
    all_questions.extend(questions)

    # Rate limit 방지
    time.sleep(1)

# 📌 결과 저장
with open(output_path, "w", encoding="utf-8") as f:
    for idx, question in enumerate(all_questions, start=1):
        f.write(f"{idx}. {question}\n")

print(f"✅ LLM 기반 질문 {len(all_questions)}개 생성 완료! 저장 위치: {output_path}")