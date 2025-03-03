import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('jhgan/ko-sbert-sts')

def get_embedding(text):
    return embedding_model.encode(text)

def split_into_sentences(transcript):
    return [s.strip() for s in transcript.split('\n') if s.strip()]

def split_into_segments(sentences, window_size=3):
    return [" ".join(sentences[i:i+window_size]) for i in range(len(sentences) - window_size + 1)]

def get_top_segments(question_embedding, sentences, top_k=5, window_size=3):
    segments = split_into_segments(sentences, window_size)
    segment_embeddings = np.array([get_embedding(s) for s in segments])
    similarities = cosine_similarity([question_embedding], segment_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [segments[i] for i in top_indices]

def fetch_similar_questions(question_embedding, records, top_k=3):
    embeddings = np.array([r['embedding'] for r in records])
    similarities = cosine_similarity([question_embedding], embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    return [records[i] for i in top_indices]
