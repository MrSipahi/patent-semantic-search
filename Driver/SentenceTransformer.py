
from sentence_transformers import SentenceTransformer

class STBert:
    def __init__(self,model) -> None:
        self.model = SentenceTransformer(model)
    
    def encode(self, text):
        return self.model.encode(text)