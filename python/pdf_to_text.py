import fitz  # PyMuPDF
import json

def extract_text_from_pdf(pdf_path):
    """PDF에서 텍스트를 추출하는 함수"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")  # 'text' 모드는 레이아웃을 무시하고 텍스트만 추출
    return text

# PDF 경로
pdf_paths = [
    "C:/Users/tyumi/Desktop/side_pjt/Samsung_guide_1.pdf",
    "C:/Users/tyumi/Desktop/side_pjt/Samsung_guide_2.pdf"
]

# PDF 텍스트 추출 및 JSON 저장
data = []

for idx, pdf_path in enumerate(pdf_paths):
    pdf_text = extract_text_from_pdf(pdf_path)
    data.append({
        "category": f"Samsung Guide {idx+1}",  # 문서별 구분
        "text": pdf_text
    })

# JSON 파일로 저장
json_path = "C:/Users/tyumi/Desktop/side_pjt/Samsung_guides.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"📁 JSON 저장 완료: {json_path}")
