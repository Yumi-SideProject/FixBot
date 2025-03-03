from openai import OpenAI
from FixBot.FixBot.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_final_answer(question, initial_answer, context):
    prompt = f"""
    다음은 유튜브에서 추출한 정보와 보완 답변입니다.
    질문: {question}
    참고 정보:
    {context}

    보완 답변:
    {initial_answer}

    위 정보를 기반으로 사용자에게 친절하고 정확한 답변을 작성해주세요.
    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "당신은 삼성 가전제품 전문가입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()
