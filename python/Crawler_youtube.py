from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json

# 📌 검색어 리스트
search_terms = [
    "삼성 세탁기 통세척",
    "삼성 세탁기 배수필터 청소",
    "삼성 세탁기 탈수가 안될때",
    "삼성 세탁기 세제통 청소",
    "삼성 세탁기 사용법",
    "삼성 세탁기 청소 방법",
    "삼성 세탁기 건조기 청소"
]

# 📌 크롬 드라이버 설정
options = Options()
options.add_argument("--headless")  # UI 없이 실행
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 📌 WebDriver 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 📌 전체 결과 저장
all_videos = []

# ✅ 검색어별 크롤링 수행
for term in search_terms:
    print(f"\n🔍 검색어: {term}")
    
    search_url = f"https://m.youtube.com/results?search_query={term.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(3)  # 로딩 대기

    # 📌 개별 검색어 결과 저장
    videos = []

    # ✅ Shorts 크롤링
    shorts_elements = driver.find_elements(By.XPATH, "//ytm-shorts-lockup-view-model-v2//a[contains(@href, '/shorts/')]")
    for short in shorts_elements:
        url = short.get_attribute("href")
        title = short.get_attribute("title").strip() if short.get_attribute("title") else short.text.strip()
        if url and title:
            videos.append({"title": title, "url": url, "type": "Shorts"})

    # ✅ 일반 동영상 크롤링
    video_elements = driver.find_elements(By.XPATH, "//ytd-video-renderer//a[contains(@href, '/watch')]")
    for video in video_elements:
        url = video.get_attribute("href")
        title = video.get_attribute("title").strip() if video.get_attribute("title") else video.text.strip()
        if url and title:
            videos.append({"title": title, "url": url, "type": "Video"})

    # 📌 중복 제거 (URL 기준)
    unique_videos = {video["url"]: video for video in videos}.values()
    
    # 📌 검색어별 수집된 개수 및 제목 목록 출력
    print(f"✅ {term} - {len(unique_videos)}개 수집 완료!")
    for video in unique_videos:
        print(f"   ▶ {video['title']}")

    # 📌 전체 리스트에 추가
    all_videos.extend(unique_videos)

# 📌 JSON 저장
output_file = "C:/Users/tyumi/Desktop/side_pjt/youtube_videos.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_videos, f, ensure_ascii=False, indent=4)

print(f"\n🎉 모든 검색어 크롤링 완료! 총 {len(all_videos)}개 동영상 수집됨.")
print(f"🔗 JSON 파일 저장 위치: {output_file}")

# 📌 WebDriver 종료
driver.quit()
