import os
import json
import subprocess
import time

# 📌 JSON 파일 경로 (Google Drive에 저장)
drive_path = "/content/drive/MyDrive/FixBot"
os.makedirs(drive_path, exist_ok=True)

json_file_path = os.path.join(drive_path, "youtube_videos.json")
stt_results_path = os.path.join(drive_path, "stt_results.json")
stt_temp_path = os.path.join(drive_path, "stt_results_temp.json")

# 📌 JSON 파일 로드
with open(json_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 📌 유효한 URL 필터링 (단축 URL 제외)
valid_urls = [video["url"] for video in data if "url" in video and video["url"].startswith("https")]

# 📌 yt-dlp와 whisper 설치 (Colab 환경 등에서 실행 시 필요)
os.system("pip install yt-dlp openai-whisper")

# 📌 오디오 저장 폴더 (Google Drive)
output_folder = os.path.join(drive_path, "audio")
os.makedirs(output_folder, exist_ok=True)

# 📌 이전에 저장된 STT 결과 불러오기 (중단 방지)
if os.path.exists(stt_temp_path):
    with open(stt_temp_path, "r", encoding="utf-8") as temp_file:
        stt_results = json.load(temp_file)
        processed_urls = {entry["url"] for entry in stt_results}  # 이미 처리된 URL 저장
        print(f"✅ 기존 STT 데이터 로드됨: {len(stt_results)}개 완료된 URL 감지")
else:
    stt_results = []
    processed_urls = set()

# 📌 URL별로 오디오 다운로드 및 STT 처리
for url in valid_urls:
    if url in processed_urls:
        print(f"⏭️ 이미 처리된 URL: {url}, 건너뜀")
        continue  # 중복 실행 방지

    try:
        video_id = url.split("/")[-1]  # 유튜브 ID 추출
        audio_path = os.path.join(output_folder, f"{video_id}.mp3")

        print(f"🔹 다운로드 중: {url}")
        subprocess.run(["yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "mp3", "-o", audio_path, url], check=True)

        print(f"🎙️ 음성 인식 중: {audio_path}")
        result = subprocess.run(["whisper", audio_path, "--model", "medium", "--language", "Korean"], capture_output=True, text=True)
        transcript_text = result.stdout

        # 결과 저장
        stt_results.append({"url": url, "transcript": transcript_text})
        processed_urls.add(url)  # 처리 완료된 URL 저장

        # ✅ 중간 결과 저장 (GPU 끊김 대비)
        with open(stt_temp_path, "w", encoding="utf-8") as temp_file:
            json.dump(stt_results, temp_file, ensure_ascii=False, indent=4)
            print(f"💾 중간 저장 완료: {stt_temp_path}")

    except Exception as e:
        print(f"❌ 오류 발생: {url}, {e}")

# 📌 최종 JSON 결과 저장
with open(stt_results_path, "w", encoding="utf-8") as json_file:
    json.dump(stt_results, json_file, ensure_ascii=False, indent=4)

print(f"✅ STT 완료! 최종 JSON 파일 저장됨: {stt_results_path}")
print(f"🔄 중간 저장 파일 삭제: {stt_temp_path}")
os.remove(stt_temp_path)  # 중간 저장 파일 삭제