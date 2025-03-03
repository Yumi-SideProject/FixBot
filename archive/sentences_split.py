import json
import re
import nltk
from nltk.tokenize import sent_tokenize
import unicodedata

# NLTK 문장 분할 라이브러리 다운로드
nltk.download('punkt')

# 📌 JSON 파일 로드
json_path = "C:/Users/tyumi/Desktop/side_pjt/stt/stt_results.json"
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# 📌 불필요한 문장 제거 (오류 메시지, 시스템 로그, 파일 경로 등)
def is_valid_sentence(sentence):
    # 시스템 오류 관련 문장 필터링
    error_patterns = [
        r"Skipping .* due to OSError",  # 예: "Skipping /path/file.mp3 due to OSError"
        r"Operation not supported",  # 예: "Operation not supported"
        r"Traceback.*",  # 예: Traceback 에러 메시지
        r"File \".*\", line \d+",  # 예: "File 'script.py', line 23"
        r"SyntaxError",  # 파이썬 에러 메시지
        r"OSError",  # OS 관련 에러 메시지
        r"Permission denied",  # 접근 권한 오류
        r"Downloading:",  # yt-dlp 다운로드 메시지
        r"Converting:",  # 변환 과정에서 출력되는 로그
        r"File saved at",  # 파일 저장 로그
        r"Error:",  # 일반적인 오류 문구
        r"stderr",  # 시스템 로그 관련
        r"stdout",  # 시스템 로그 관련
    ]
    for pattern in error_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            return False  # 오류 문장 제거
    return True

# 📌 깨진 문자 및 불필요한 특수문자 제거
def clean_text(text):
    # 유니코드 정규화 (복잡한 특수문자를 일반 문자로 변환)
    text = unicodedata.normalize("NFKC", text)

    # 타임스탬프 제거 [00:00.000 --> 00:03.200] 형식
    text = re.sub(r'\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]', '', text)

    # 불필요한 광고 문구 제거
    remove_phrases = [
        "구독과 좋아요 부탁드립니다", "구독", "좋아요", "시청해 주셔서 감사합니다",
        "영상 끝까지 시청해주세요", "알람 설정", "채널", "댓글 남겨주세요"
    ]
    for phrase in remove_phrases:
        text = text.replace(phrase, '')

    # 특수문자 제거 (한글, 영어, 숫자, 주요 구두점 제외)
    text = re.sub(r'[^가-힣A-Za-z0-9.,!?\'"~@#$%^&*()<>;:/+=_\-]', ' ', text)

    # 불필요한 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# 📌 문장 단위로 분할 및 정제
cleaned_data = []
for item in data:
    text = item.get("transcript", "").strip()  # 텍스트 가져오기

    # 1️⃣ 단락 기준으로 나누기
    paragraphs = text.split("\n")

    for para in paragraphs:
        para = clean_text(para)  # 텍스트 정제
        if not para or len(para) < 5:  # 빈 문자열 및 너무 짧은 텍스트 제외
            continue

        # 2️⃣ 문장 단위로 다시 분할
        sentences = sent_tokenize(para)

        for sentence in sentences:
            if len(sentence) > 10 and is_valid_sentence(sentence):  # 오류 메시지 필터링
                cleaned_data.append({"sentence": sentence})  # 개별 문장 저장

# 📌 정제된 JSON 데이터 저장
output_path = "C:/Users/tyumi/Desktop/side_pjt/stt/cleaned_sentences.json"
with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump(cleaned_data, out_file, ensure_ascii=False, indent=4)

print(f"✅ 문장 정제 완료! 파일 저장 위치: {output_path}")
