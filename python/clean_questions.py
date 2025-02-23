from sentence_transformers import SentenceTransformer, util
import re

# ✅ 사전 학습된 BERT 임베딩 모델 로드 (한글 지원)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def read_questions(file_path):
    """파일에서 질문을 읽어 리스트로 변환"""
    questions = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # 숫자/알파벳 인덱스 제거 후 질문만 추출
            match = re.search(r"[\w]\.\s*(.+)", line.strip())
            if match:
                questions.append(match.group(1))
    return questions

def remove_duplicate_questions(questions, threshold=0.9):
    """유사도가 높은 질문을 제거하여 중복 없는 리스트 생성"""
    embeddings = model.encode(questions, convert_to_tensor=True)
    similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)

    unique_questions = []
    seen_indices = set()

    for i, question in enumerate(questions):
        if i in seen_indices:
            continue
        unique_questions.append(question)
        for j in range(len(questions)):
            if i != j and similarity_matrix[i][j] > threshold:  # 유사도 기준 0.85
                seen_indices.add(j)

    return unique_questions

def save_questions(file_path, questions):
    """정제된 질문을 새로운 파일에 저장"""
    with open(file_path, "w", encoding="utf-8") as file:
        for idx, question in enumerate(questions, start=1):
            file.write(f"{idx}. {question}\n")

# ✅ 실행
input_file = "C:/Users/tyumi/Desktop/side_pjt/Samsung_generated_questions.txt"
output_file = "C:/Users/tyumi/Desktop/side_pjt/Samsung_cleaned_questions.txt"

questions = read_questions(input_file)
unique_questions = remove_duplicate_questions(questions)
save_questions(output_file, unique_questions)

print(f"✅ 정제된 질문 {len(unique_questions)}개를 {output_file}에 저장 완료!")
