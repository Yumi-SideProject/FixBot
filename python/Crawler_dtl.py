from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 크롬 드라이버 설정 (버전 자동 맞추기)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # UI 없이 실행
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriver 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# CSV에서 URL 목록 불러오기
df = pd.read_csv("C:/Users/tyumi/Desktop/side_pjt/samsung_solutions.csv")  # 파일 경로 수정 필요
urls = df["link"].tolist()

# 결과 저장 리스트
data = []

for url in urls:
    print(f"크롤링 중: {url}")
    driver.get(url)
    time.sleep(3)  # 페이지 로딩 대기

    try:
        # 본문 텍스트 추출
        content_element = driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/div')
        content = content_element.text.strip() if content_element else "내용 없음"

        # 동영상 URL 추출
        try:
            video_element = driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/div/div/div/div[1]/iframe')
            video_url = video_element.get_attribute("src") if video_element else "동영상 없음"
        except:
            video_url = "동영상 없음"

        # 결과 저장
        data.append({"URL": url, "본문": content, "동영상": video_url})

    except Exception as e:
        print(f"크롤링 실패: {url} -> {e}")
        data.append({"URL": url, "본문": "오류", "동영상": "오류"})

# 크롬 드라이버 종료
driver.quit()

# 데이터 저장 (CSV)
output_df = pd.DataFrame(data)
output_df.to_csv("C:/Users/tyumi/Desktop/side_pjt/samsung_solutions_scraped.csv", index=False, encoding="utf-8-sig")

print("크롤링 완료! CSV 파일로 저장됨.")