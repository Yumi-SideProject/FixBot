import json
import time
import re
import numpy as np
import faiss  # 🔥 FAISS 추가 (pip install faiss-cpu)
from groq import Groq  # 🔥 Groq API 사용
from rank_bm25 import BM25Okapi  # 🔥 BM25 추가 (pip install rank-bm25)
from sentence_transformers import SentenceTransformer  # 🔥 FAISS 벡터화 모델 (pip install sentence-transformers)

# ✅ Groq API 설정
API_KEY = "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"  # 🔥 여기에 Groq API Key 입력
client = Groq(api_key=API_KEY)  # 🔥 API Key를 사용하여 Groq 클라이언트 초기화

# ✅ 모델 정보
MODEL_NAME = "llama-3.3-70b-versatile"

# ✅ FAISS 임베딩 모델 로드 (정확도가 높은 모델 사용)
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")  # 🔥 정확도 높은 임베딩 모델 사용

# ✅ 파일 경로
SENTENCES_FILES = ["/content/FixBot/Samsung_sentences_1.json", "/content/FixBot/Samsung_sentences_2.json"]
QUESTIONS_FILE = "/content/FixBot/Samsung_cleaned_questions.txt"
OUTPUT_FILE = "/content/FixBot/Samsung_answers.json"

# ✅ 문장 데이터 로드
def load_sentences():
    """9000개 문장을 로드하여 BM25 + FAISS 인덱스 생성"""
    sentences = []
    for file_path in SENTENCES_FILES:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            sentences.extend([item["sentence"] for item in data])
    return sentences

# ✅ 질문 데이터 로드
def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# ✅ `BM25` 인덱스 생성
def create_bm25_index(sentences):
    """BM25를 위한 문장 인덱스 생성"""
    tokenized_sentences = [re.findall(r'\w+', s.lower()) for s in sentences]  # 🔥 토큰화
    return BM25Okapi(tokenized_sentences), tokenized_sentences

# ✅ `FAISS` 인덱스 생성
def create_faiss_index(sentences):
    sentence_embeddings = embedding_model.encode(sentences, convert_to_numpy=True)
    d = sentence_embeddings.shape[1]

    index = faiss.IndexFlatL2(d)  # L2 거리 기반 검색
    index.add(sentence_embeddings)

    # 🔥 검색 성능 향상 (탐색 반경 확장)
    index.nprobe = 20
    return index, sentence_embeddings

# ✅ `BM25 + FAISS` 기반 관련 문장 찾기
def find_relevant_sentences(question, bm25, sentences, tokenized_sentences, faiss_index, sentence_embeddings, top_n=10):
    """BM25와 FAISS를 결합하여 관련 문장 검색"""
    
    # 🔥 1️⃣ BM25 검색 (질문과 키워드가 유사한 상위 100개 문장 선택)
    tokenized_query = re.findall(r'\w+', question.lower())
    bm25_scores = bm25.get_scores(tokenized_query)
    top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:100]
    bm25_selected_sentences = [sentences[i] for i in top_bm25_indices]

    if not bm25_selected_sentences:
        print(f"⚠️ BM25에서 관련 문장을 찾지 못했습니다: {question}")
        return []

    # 🔥 2️⃣ FAISS 검색 (BM25 상위 100개 문장 중 가장 유사한 10개 문장 선택)
    query_embedding = embedding_model.encode([question], convert_to_numpy=True)
    _, faiss_indices = faiss_index.search(query_embedding, top_n)

    if len(faiss_indices[0]) == 0:
        print(f"⚠️ FAISS에서 관련 문장을 찾지 못했습니다: {question}")
        
        # 🔥 FAISS가 실패했을 경우, BM25 결과를 FAISS 인덱스에 추가 후 재검색
        faiss_index.add(embedding_model.encode(bm25_selected_sentences, convert_to_numpy=True))
        _, faiss_indices = faiss_index.search(query_embedding, top_n)

        if len(faiss_indices[0]) == 0:
            print(f"⚠️ FAISS 재검색 실패, BM25 문장 사용: {question}")
            return bm25_selected_sentences[:top_n]  # BM25 결과 반환

    # 🔥 최종 문장 선택
    final_selected_sentences = [bm25_selected_sentences[i] for i in faiss_indices[0] if i < len(bm25_selected_sentences)]
    
    if not final_selected_sentences:
        print(f"⚠️ FAISS 검색 결과 없음, BM25 문장 사용: {question}")
        return bm25_selected_sentences[:top_n]

    return final_selected_sentences

# ✅ Groq API를 이용한 답변 생성 (LLM 프롬프트 개선)
def generate_answer(question, relevant_sentences):
    """Groq API를 사용하여 답변 생성"""
    if not relevant_sentences:
        return "관련된 정보를 찾을 수 없습니다. 고객센터에 문의하세요."

    # 🔥 LLM 프롬프트 개선 (직접적인 답변 유도)
    prompt = f"""
    ## 너의 목적:
    - **고객들에게 유용한 정보를 제공한다.**
    - **고객들이 처한 문제 상황에서 적절한 해결책을 정확한 출처/자료 기반으로 제시한다.**

    ## 질문:
    {question}

    ## 관련 문서:
    {' '.join(relevant_sentences)}

    ## 답변:
    - **질문에 대한 구체적인 해결 방법 자세히 설명하세요.**
    - **관련 없는 정보는 절대로 포함하지 마세요.**
    - **정확하고 명확한 해결 방법을 제시하세요.**
    - **주부 고객들이 이해하기 쉽게 설명하세요.**
    - **고객들이 가장 쉽고 편하게 해결할 수 있는 방법을 우선으로 설명하세요.**
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # 🔥 답변을 더 정확하게
        max_tokens=2000,  # 🔥 너무 긴 답변 방지
        top_p=0.85,  # 🔥 품질 최적화
        stream=False
    )

    return response.choices[0].message.content.strip()

# ✅ 전체 질문 처리 및 답변 생성
def process_questions():
    sentences = load_sentences()
    questions = load_questions()

    # 🔥 `BM25` + `FAISS` 인덱스 생성
    bm25, tokenized_sentences = create_bm25_index(sentences)
    faiss_index, sentence_embeddings = create_faiss_index(sentences)

    answers = []
    for idx, question in enumerate(questions):
        print(f"📝 질문 {idx+1}/{len(questions)}: {question}")

        # 관련 문장 찾기 (`BM25 + FAISS` 활용)
        relevant_sentences = find_relevant_sentences(question, bm25, sentences, tokenized_sentences, faiss_index, sentence_embeddings)

        # LLM을 활용해 답변 생성
        answer = generate_answer(question, relevant_sentences)
        print('--------------')
        print(answer)
        print('--------------')

        # 결과 저장
        answers.append({"question": question, "answer": answer})

        # Rate limit 방지
        time.sleep(2)

    # JSON으로 저장
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 답변 저장 완료: {OUTPUT_FILE}")

# ✅ 실행
if __name__ == "__main__":
    process_questions()
