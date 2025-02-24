import json
import requests
import time

# ✅ Llama API 설정
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = "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"  # 🔥 API 키 설정 필요
MODEL = "llama-3.3-70b-versatile"
OUTPUT_FILE = "/content/llm_filtered_sentences.json"

# ✅ JSON 파일 로드
def load_json_files(file_paths):
    sentences = []
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            sentences.extend([item["sentence"] for item in data])
    return list(sentences)  # 중복 제거

# ✅ Llama API 요청 함수
def call_llama_api(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        print(f"❗ API 호출 오류: {response.status_code}")
        return None

# ✅ 프롬프트 생성
def generate_prompt(sentences):
    return (
        "아래 문장이 제품의 **문제 해결 방법** 또는 **설정 가이드**인지 판별해 주세요.\n"
        "- 해결 방법일 경우, 그대로 유지\n"
        "- 해결 방법이 아니라면 제외\n"
        "- 해결 방법이 여러 문장으로 이루어진 경우, 연결된 문장들을 함께 유지\n"
        "- 단순한 제품 설명이나 기능 소개 문장은 제외\n"
        "- 별도의 앞뒤 내용 없이 해당 내용만 출력.\n"
        "- nutshell, for slack message, in korean\n\n"
        "문장 리스트:\n" + "\n".join(sentences)
    )

# ✅ Llama API를 활용한 문장 필터링
def filter_sentences(sentences, batch_size=50):
    filtered_sentences = []
    
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i : i + batch_size]
        prompt = generate_prompt(batch)

        response = call_llama_api(prompt)
        if response:
            print(response)  # 필터링된 응답 출력 (디버깅)
            filtered_sentences.extend(response.split("\n"))

        # Rate Limit 방지 (랜덤 대기)
        time.sleep(3 + int(time.time()) % 2)

    return filtered_sentences

# ✅ 결과 저장
def save_to_json(sentences, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([{"sentence": s} for s in sentences], f, ensure_ascii=False, indent=4)
    print(f"✅ 필터링된 문장 저장 완료: {output_file}")

# ✅ 실행 코드
if __name__ == "__main__":
    file_paths = ["/content/Samsung_sentences_1.json", "/content/Samsung_sentences_2.json"]

    sentences = load_json_files(file_paths)
    print(f"📌 원본 문장 개수: {len(sentences)}")

    filtered_sentences = filter_sentences(sentences)
    print(f"✅ 필터링 후 문장 개수: {len(filtered_sentences)}")

    save_to_json(filtered_sentences, OUTPUT_FILE)
