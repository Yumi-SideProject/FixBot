from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 크롬 드라이버 설정 (버전 자동 맞추기)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # UI 없이 실행하려면 활성화
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# WebDriver 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 크롤링할 URL
base_url = "https://www.samsungsvc.co.kr/solution?category=10471&product=10502"
driver.get(base_url)

# 결과 저장할 리스트
data = []

# 총 34페이지 순회
for page in range(1, 35):  # 1부터 34까지
    print(f"현재 페이지: {page}")

    # 현재 페이지에서 게시물 크롤링
    elements = driver.find_elements(By.XPATH, '//*[@id="content"]/div[4]/div[2]/ul/li/div[1]/a')
    
    for elem in elements:
        href = elem.get_attribute("href")
        text = elem.text.strip()
        if href and text:
            data.append({"title": text, "link": href})

    # 다음 페이지 이동 (마지막 페이지가 아닐 때)
    if page < 34:
        try:
            next_button = driver.find_element(By.XPATH, '//*[@id="content"]/div[4]/div[2]/div/a[3]')
            next_button.click()
            time.sleep(2)  # 페이지 로딩 대기
        except Exception as e:
            print(f"페이지 이동 중 오류 발생: {e}")
            break  # 오류 발생 시 크롤링 중단

# 크롬 드라이버 종료
driver.quit()

# 데이터 저장 (CSV)
df = pd.DataFrame(data)
df.to_csv("C:/Users/tyumi/Desktop/side_pjt/samsung_solutions.csv", index=False, encoding="utf-8-sig")

print("크롤링 완료! CSV 파일로 저장됨.")