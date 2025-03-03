import re

def clean_question(text):
    # 화살표 기준 왼쪽만 남김
    if '→' in text:
        text = text.split('→')[0].strip()
    elif '->' in text:
        text = text.split('->')[0].strip()

    # 앞뒤 특수문자 제거
    text = text.strip().strip('"').strip('*').strip()

    # 특정 영어 안내 문구 삭제
    if "I'm ready to help!" in text:
        return None

    return text.strip()
