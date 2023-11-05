from Driver.SentenceTransformer import STBert


class VectorEmbeddingProvider:
    def __init__(self,model) -> None:
        self.model= model
        self.vector_embedding = STBert(model)
    
    def encode (self, text):
        return self.vector_embedding.encode(text)
    
