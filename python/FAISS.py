import json
import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# 🚀 1. JSON 파일 로드
file_paths = ["C:/Users/tyumi/Desktop/side_pjt/Samsung_sentences_1.json", "C:/Users/tyumi/Desktop/side_pjt/Samsung_sentences_2.json"]

all_sentences = []
for file_path in file_paths:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        all_sentences.extend([item["sentence"] for item in data])

print(f"✅ 문장 개수: {len(all_sentences)}")

# 🚀 2. SBERT 모델 로드 (경량화 모델 사용)
model_name = "paraphrase-mpnet-base-v2"  # 정확도 우선 모델
device = "cuda" if torch.cuda.is_available() else "cpu"  # GPU 사용 가능하면 CUDA 적용
print(f"✅ 사용 디바이스: {device}")

model = SentenceTransformer(model_name, device=device)

# 🚀 3. 문장 벡터화 (Batch 처리)
batch_size = 32  # 한 번에 처리할 문장 개수
sentence_embeddings = []

for i in range(0, len(all_sentences), batch_size):
    batch = all_sentences[i:i+batch_size]
    batch_embeddings = model.encode(batch, batch_size=batch_size, convert_to_tensor=True, device=device)
    sentence_embeddings.append(batch_embeddings.cpu().numpy())  # GPU 사용 시 CPU로 변환

# 모든 벡터 합치기
sentence_embeddings = np.vstack(sentence_embeddings)

# 🚀 4. FAISS 인덱스 생성 (내적곱 기반)
vector_dim = sentence_embeddings.shape[1]
faiss_index = faiss.IndexFlatIP(vector_dim)  # 내적곱 기반
faiss_index.add(np.array(sentence_embeddings, dtype=np.float32))

# 🚀 5. FAISS 인덱스 저장
faiss.write_index(faiss_index, "C:/Users/tyumi/Desktop/side_pjt/samsung_faiss.index")
print("✅ FAISS 인덱스 저장 완료!")

# 🚀 6. 검색 예제
query = "세탁기 초기화 방법"
query_vector = model.encode([query], normalize_embeddings=True, convert_to_tensor=True, device=device)
query_vector = query_vector.cpu().numpy()  # GPU 사용 시 변환

D, I = faiss_index.search(np.array(query_vector, dtype=np.float32), k=3)  # 상위 3개 검색

print("\n🎯 검색 결과:")
for idx in I[0]:
    print(f"- {all_sentences[idx]}")
