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
    error_patterns = [
        r"Skipping .* due to OSError",
        r"Operation not supported",
        r"Traceback.*",
        r"File \".*\", line \d+",
        r"SyntaxError",
        r"OSError",
        r"Permission denied",
        r"Downloading:",
        r"Converting:",
        r"File saved at",
        r"Error:",
        r"stderr",
        r"stdout",
    ]
    for pattern in error_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            return False
    return True

# 📌 깨진 문자 및 불필요한 특수문자 제거
def clean_text(text):
    text = unicodedata.normalize("NFKC", text)

    # 타임스탬프 제거
    text = re.sub(r'\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]', '', text)

    # 광고성 문구 제거
    remove_phrases = [
        "구독과 좋아요 부탁드립니다", "구독", "좋아요", "시청해 주셔서 감사합니다",
        "영상 끝까지 시청해주세요", "알람 설정", "채널", "댓글 남겨주세요"
    ]
    for phrase in remove_phrases:
        text = text.replace(phrase, '')

    # 특수문자 제거 (한글, 영어, 숫자, 주요 구두점 제외)
    text = re.sub(r'[^가-힣A-Za-z0-9.,!?\'"~@#$%^&*()<>;:/+=_\-]', ' ', text)

    # 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# 📌 문장 정제 및 저장 구조 변경 (출처 URL, 제목, 정제된 문장)
cleaned_data = []
for item in data:
    url = item.get("url", "")
    transcript = item.get("transcript", "").strip()
    paragraphs = transcript.split("\n")
    for para in paragraphs:
        para = clean_text(para)
        if not para or len(para) < 5:
            continue

        sentences = sent_tokenize(para)
        for sentence in sentences:
            if len(sentence) > 10 and is_valid_sentence(sentence):
                cleaned_data.append({
                    "url": url,
                    "sentence": sentence
                })

# 📌 정제된 JSON 데이터 저장
output_path = "C:/Users/tyumi/Desktop/side_pjt/stt/cleaned_sentences_saved.json"
with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump(cleaned_data, out_file, ensure_ascii=False, indent=4)

print(f"✅ 문장 정제 완료! 파일 저장 위치: {output_path}")
