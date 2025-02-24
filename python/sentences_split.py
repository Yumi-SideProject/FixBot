import json
import re
import nltk
from nltk.tokenize import sent_tokenize
import unicodedata

# NLTK 문장 분할을 위한 라이브러리 다운로드
nltk.download('punkt')

# JSON 파일 로드
json_path = "C:/Users/tyumi/Desktop/side_pjt/Samsung_merged_data.json" #Samsung_guides
with open(json_path, "r", encoding="utf-8", errors="ignore") as file:
    data = json.load(file)

# 깨진 문자 및 비정상적인 문자 필터링
def remove_invalid_chars(text):
    # 유니코드 정규화 (NFKC) -> 복잡한 특수문자를 일반 텍스트로 변환
    text = unicodedata.normalize("NFKC", text)

    # 제어 문자(컨트롤 문자) 제거 (\u0000-\u001F, \u007F-\u009F)
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', text)

    # 한글, 영어, 숫자, 일반적인 구두점(.,!?'"~@#$%^&*()-_+=)만 허용
    text = re.sub(r'[^가-힣A-Za-z0-9.,!?\'"~`@#$%^&*()<>;:/+=_\-]', ' ', text)

    return text.strip()

# 데이터 정제 함수
def clean_text(text):
    text = remove_invalid_chars(text)  # 깨진 문자 제거
    text = text.replace("\n", " ")  # 개행 문자 제거
    text = re.sub(r'\s+', ' ', text)  # 연속된 공백 제거
    text = re.sub(r'[-=+#/\:;^@*※~ㆍ!』\[\]{}()]', '', text)  # 특수문자 제거
    text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)  # 날짜 패턴 제거
    text = re.sub(r'\b[가-힣]+\s?(경고|주의)\b', '', text)  # "경고" 또는 "주의" 단어 제거
    text = re.sub(r'(?i)shorts|비디오|동영상', '', text)  # 광고성 문구 제거
    return text.strip()

# 정제 및 문장 단위 분할
cleaned_data = []
for item in data:
    text = item.get("text", "").strip()  # 텍스트 가져오기

    # 개행 기준으로 단락 분할
    paragraphs = text.split("\n")

    for para in paragraphs:
        para = clean_text(para)  # 텍스트 정제
        if not para or len(para) < 5:  # 빈 문자열 및 너무 짧은 텍스트 제외
            continue

        # 문장 단위로 다시 분할
        sentences = sent_tokenize(para)

        for sentence in sentences:
            if len(sentence) > 10:  # 너무 짧거나 의미 없는 문장 제거
                cleaned_data.append({"sentence": sentence})  # 개별 문장 저장

# 결과 출력 예시 (상위 5개 문장만 확인)
for idx, doc in enumerate(cleaned_data[:5]):
    print(f"{idx+1}. {doc['sentence']}")
    print("----\n")

# 정제된 JSON 데이터 저장
output_path = "C:/Users/tyumi/Desktop/side_pjt/Samsung_sentences_1.json" #Samsung_sentences_2
with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump(cleaned_data, out_file, ensure_ascii=False, indent=4)

print(f"✅ 정제된 데이터가 {output_path}에 저장되었습니다.")