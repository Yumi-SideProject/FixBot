import re
from konlpy.tag import Okt
from langdetect import detect
import json

# 한국어 NLP
okt = Okt()

# 질문을 나타내는 패턴 목록
question_patterns = [
    "어떻게", "무엇", "언제", "어디", "왜", "어떤", "누가", "누구", "얼마",
    "할 수 있나요", "가능한가요", "될까요", "되나요",
    "방법", "사용법", "설치 방법", "초기 설정", "설명해 주세요", "알려 주세요",
    "자세히 알려주세요", "차이가 뭔가요", 
    "추천해 주세요", "비교해 주세요", "어떤 게 더 좋은가요",
    "가격이 얼마인가요", "성능이 어떤가요", "최대 용량이 얼마인가요",
    "오류 코드", "고장났어요", "수리하려면", "고장났을 때",
    "필요한가요", "등록해야 하나요", "업데이트 해야 하나요"
]

def is_question(text):
    """문장이 질문인지 확인하는 함수"""
    if "?" in text:  # 물음표 포함 여부
        return True

    # 질문 패턴 포함 여부
    for pattern in question_patterns:
        if pattern in text:
            return True

    return False

def clean_text(text):
    """불필요한 특수 문자와 공백을 정리하는 함수"""
    text = re.sub(r'[\n•\t]', ' ', text)  # 줄바꿈 및 불필요한 기호 제거
    text = re.sub(r'\s+', ' ', text).strip()  # 연속 공백 제거
    return text

def extract_questions(text):
    """텍스트에서 의문문(질문)만 추출하는 함수"""
    sentences = re.split(r'(?<=[.!?])\s+|[\n•\-]', text)  # 문장 분리 개선
    questions = []

    for sent in sentences:
        try:
            sent = clean_text(sent)  # 텍스트 정리
            if len(sent) < 5:  # 너무 짧은 문장은 제외
                continue
            lang = detect(sent)  # 언어 감지
            if lang == "ko":  # 한국어 문장만 처리
                if is_question(sent):
                    questions.append(sent)
        except:
            pass  # 언어 감지 실패 시 무시

    return questions

# JSON 파일 경로
guides_path = "C:/Users/tyumi/Desktop/side_pjt/Samsung_guides.json"
merged_data_path = "C:/Users/tyumi/Desktop/side_pjt/Samsung_merged_data.json"

# JSON 파일 로드
with open(guides_path, "r", encoding="utf-8") as f:
    guides_data = json.load(f)

with open(merged_data_path, "r", encoding="utf-8") as f:
    merged_data = json.load(f)

# 결과 저장 리스트
questions_list = []

# guides_data 따로 처리
for doc in guides_data:
    text = doc.get("text", "")

    # 특수문자로 문장 분리
    sentences = re.split(r'[.!?•\n\-]', text)
    cleaned_sentences = [clean_text(sent) for sent in sentences if len(sent) > 5]
    
    questions = [sent for sent in cleaned_sentences if is_question(sent)]
    
    questions_list.extend(questions)  # 리스트에 추가

# merged_data 따로 처리
for doc in merged_data:
    category = doc.get("category", "Unknown")
    text = doc.get("text", "")

    combined_text = f"{category} {text}"  # category + text 합침
    questions = extract_questions(combined_text)

    questions_list.extend(questions)  # 리스트에 추가

# 리스트 형식으로 저장
questions_txt_path = "C:/Users/tyumi/Desktop/side_pjt/Samsung_questions.txt"
with open(questions_txt_path, "w", encoding="utf-8") as f:
    for question in questions_list:
        f.write(question + "\n")

print(f"✅ 질문 추출 완료! 텍스트 파일 저장: {questions_txt_path}")
