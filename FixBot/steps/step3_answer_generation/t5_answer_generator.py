from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# pko-t5 모델 로드
tokenizer = AutoTokenizer.from_pretrained("paust/pko-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("paust/pko-t5-base")

def generate_t5_answer(question, context):
    prompt = f"질문: {question}\n답변을 위해 참고할 정보:\n{context}\n\n위 정보를 기반으로 답변을 작성하세요."
    
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        max_length=2048,  # ✅ 입력 길이 확장
        truncation=True
    )
    
    outputs = model.generate(
        **inputs,
        max_length=512,   # ✅ 출력 길이 확장
        temperature=0.7,  # ✅ 답변 다양성 확보
        do_sample=True    # ✅ 일부 랜덤성 추가해 답변 단조로움 방지
    )
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
