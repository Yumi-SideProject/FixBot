from sentence_transformers import SentenceTransformer

def load_embedding_model():
    return SentenceTransformer('jhgan/ko-sbert-sts')

def get_embedding(model, text):
    return model.encode(text).tolist()
