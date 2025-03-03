import json
from sentence_transformers import SentenceTransformer
from supabase import create_client
import os
from datetime import datetime
import re
from FixBot.config import SUPABASE_URL, SUPABASE_KEY

# 경로 설정 (디렉토리 구조 맞춰서 변경)
DATA_PATH = 'C:/workspace/FixBot/data/Samsung_answers.json'

# 모델 로드 (한국어 문장 임베딩 지원 모델)
model = SentenceTransformer('jhgan/ko-sbert-sts')

# Supabase 클라이언트 생성
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 데이터 로드
with open(DATA_PATH, 'r', encoding='utf-8') as file:
    samsung_data = json.load(file)

def clean_question(text):
    # "숫자. " 또는 "숫자. 숫자. " 패턴 제거
    cleaned_text = re.sub(r'^\d+(\.\s*)?(\d+\.\s*)?', '', text).strip()
    return cleaned_text

# 데이터 정제 & 업로드
for item in samsung_data:
    raw_question = item.get('question', '').strip()
    answer = item.get('answer', '').strip()

    # 질문 정제
    cleaned_question = clean_question(raw_question)

    # 임베딩 생성
    embedding = model.encode(cleaned_question).tolist()

    # Supabase 저장 데이터 구성
    data = {
        'question': cleaned_question,
        'answer': answer,
        'embedding': embedding,
        'created_at': datetime.now().isoformat()
    }

    # 데이터 업로드 (최신 방식 - try-except로 처리)
    try:
        response = supabase.table('samsung_qna').insert(data).execute()
        print(f"✅ 저장 성공: {cleaned_question}")
    except Exception as e:
        print(f"❌ 저장 실패: {cleaned_question}, 에러: {e}")