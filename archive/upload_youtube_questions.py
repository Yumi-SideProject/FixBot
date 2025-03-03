import sys
import os

# 현재 스크립트 기준으로 상위 디렉터리 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

import json
from supabase import create_client
from datetime import datetime
from FixBot.archive.embedding_utils import load_embedding_model, get_embedding
from FixBot.archive.question_cleaner import clean_question
from FixBot.FixBot.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
model = load_embedding_model()

# 유튜브 자막 데이터 로드
with open('C:/workspace/FixBot/data/cleaned_sentences_saved.json', 'r', encoding='utf-8') as file:
    youtube_data = json.load(file)

# URL별 자막 병합
transcript_by_url = {}
for item in youtube_data:
    url = item['url']
    sentence = item['sentence']
    if url not in transcript_by_url:
        transcript_by_url[url] = []
    transcript_by_url[url].append(sentence)

# 🔥 question_embedding 데이터를 Supabase에서 직접 조회
response = supabase.table('question_embeddings').select("refined_question, source").execute()
question_data = response.data  # 리스트로 바로 사용 가능

print(f"✅ Supabase에서 {len(question_data)}개 질문 데이터를 불러왔습니다.")

# 정제 및 업로드
for item in question_data:
    raw_question = item['refined_question']
    video_url = item['source']

    # 질문 정제
    cleaned_question = clean_question(raw_question)

    if cleaned_question is None:
        print(f"⚠️ 정제 제외: {raw_question}")
        continue

    # URL별 자막 병합
    transcript = "\n".join(transcript_by_url.get(video_url, []))

    # 질문 임베딩 생성
    embedding = get_embedding(model, cleaned_question)

    # Supabase 저장 데이터 구성
    data = {
        'question': cleaned_question,
        'transcript': transcript,
        'embedding': embedding,
        'video_url': video_url,
        'created_at': datetime.now().isoformat()
    }

    try:
        supabase.table('video_questions').insert(data).execute()
        print(f"✅ 저장 성공: {cleaned_question}")
    except Exception as e:
        print(f"❌ 저장 실패: {cleaned_question}, 에러: {e}")

print("✅ 모든 유튜브 데이터 업로드 완료")
