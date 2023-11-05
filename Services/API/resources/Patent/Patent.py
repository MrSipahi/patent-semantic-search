
from flask_restful import Resource, reqparse
import os
from dotenv import load_dotenv
from time import time 

from Library.VectorDB import VectorDatabaseProvider
from Library.VectorEmbedding import VectorEmbeddingProvider

class Search(Resource):
    def __init__(self):
        load_dotenv(".env")
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('query', type=str, required=True, help='Arama sorgusu girilmedi.')
        self.parser.add_argument('model', type=str, default=os.getenv("VECTOR_MODEL", "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"))
        self.parser.add_argument('limit', type=int, default=10)
        self.parser.add_argument('collection_name', type=str, default=os.getenv("MILVUS_COLLECTION", "bio_patent"))
        self.args = self.parser.parse_args()
        self.vectorDB = VectorDatabaseProvider()
        self.vector_embedding = VectorEmbeddingProvider(self.args.model)

    def post(self):
        
        embedding_time = time()
        vectors_to_search = self.vector_embedding.encode(self.args.query)
        embedding_time = time() - embedding_time

        vectors_to_search = [list(vectors_to_search)]
        

        search_params = {
            "data": vectors_to_search,
            "anns_field": "paragraph_vec",
            "param": {"metric_type": "L2", "params": {"nprobe": 10}, "offset": 0},
            "limit": self.args.limit,
            "expr": f'vector_model == "{self.args.model}"',
            "output_fields": ["id","patent_id","paragraph","title","abstract"],
            }

        search_time = time()
        result = self.vectorDB.search(self.args.collection_name,search_params)
        search_time = time() - search_time


        if len(result) == 0:
            return {'result': []},200

        sorted_result = sorted(result[0], key=lambda k: k.score, reverse=True)

        last_data = []
        for item in sorted_result:
            last_data.append({
                "id": item.id,
                "patent_id": item.patent_id,
                "paragraph": item.paragraph,
                "title": item.title,
                "abstract": item.abstract,
                "score": round(item.score,2),
            })

        return {'embedding_time': round(embedding_time,3),'search_time': round(search_time,3), 'result': last_data},200
    

class Patent(Resource):
    def __init__(self) -> None:
        load_dotenv(".env")
        self.collection_name = os.getenv("MILVUS_COLLECTION", "bio_patent")
        self.vectorDB = VectorDatabaseProvider()

    def get(self, patent_id):
        result = self.vectorDB.get(self.collection_name,patent_id)
        if len(result) == 0:
            return {"error": "Patent Not Found"},404
        else:
            return result[0],200