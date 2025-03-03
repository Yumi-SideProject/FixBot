from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# KoELECTRA 모델 로드
koelectra_tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-small-v3-discriminator")
koelectra_model = AutoModelForSequenceClassification.from_pretrained("monologg/koelectra-small-v3-discriminator", num_labels=2)

def is_valid_question(question):
    inputs = koelectra_tokenizer(question, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = koelectra_model(**inputs)
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    return predicted_class == 1