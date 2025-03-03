from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import torch

# KoELECTRA 모델 로드
koelectra_tokenizer = AutoTokenizer.from_pretrained("monologg/koelectra-small-v3-discriminator")
koelectra_model = AutoModelForSequenceClassification.from_pretrained("monologg/koelectra-small-v3-discriminator", num_labels=2)

# Sentence-BERT 모델 로드
embedding_model = SentenceTransformer('jhgan/ko-sbert-sts')

def is_valid_question(question):
    inputs = koelectra_tokenizer(question, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = koelectra_model(**inputs)
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    return predicted_class == 1

def get_embedding(text):
    return embedding_model.encode(text).tolist()
