import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# KoSimCSE 모델로 변경
embedding_model = SentenceTransformer('jhgan/ko-simcse-roberta-multitask')

def get_embedding(text):
    """문장 임베딩 생성 (KoSimCSE 사용)"""
    return embedding_model.encode(text)

def split_into_sentences(transcript):
    """자막을 문장 단위로 분할"""
    return [s.strip() for s in transcript.split('\n') if s.strip()]

def split_into_segments(sentences, window_size=3):
    """문장 리스트를 일정 길이의 세그먼트로 분할"""
    return [" ".join(sentences[i:i+window_size]) for i in range(len(sentences) - window_size + 1)]

def get_top_segments(question_embedding, sentences, top_k=2, window_size=3):
    """질문과 가장 유사한 상위 세그먼트 추출"""
    segments = split_into_segments(sentences, window_size)
    segment_embeddings = np.array([get_embedding(s) for s in segments])

    similarities = cosine_similarity([question_embedding], segment_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    return [segments[i] for i in top_indices]

def fetch_similar_questions(question_embedding, records, top_k=3, threshold=0.7):
    """질문과 의미적으로 가장 유사한 문서 상위 K개 추출 (KoSimCSE + 유사도 임계치 필터링)"""
    embeddings = np.array([r['embedding'] for r in records])
    similarities = cosine_similarity([question_embedding], embeddings)[0]

    top_indices = similarities.argsort()[-top_k:][::-1]

    filtered_matches = []
    for i in top_indices:
        if similarities[i] >= threshold:
            match = records[i]
            match['similarity'] = similarities[i]
            filtered_matches.append(match)

    return filtered_matches
