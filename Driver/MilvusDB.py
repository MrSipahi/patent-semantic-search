from pymilvus import (
    connections,
    Collection,
)
import os
from dotenv import load_dotenv

class MilvusDB:
    def __init__(self) -> None:
        db = os.getenv("MILVUS_DB", "default")
        host = os.getenv("MILVUS_HOST", "localhost")
        port = os.getenv("MILVUS_PORT", "19530")

        connections.connect(db, host=host, port=port)
    
    def search(self,collection_name:str, search_params:dict):
        col = Collection(collection_name)
        result = col.search(**search_params)
        return result
    
    def insert(self,collection_name:str, entities:list)->bool:
        col = Collection(collection_name)
        return col.insert(entities)

    def get(self, collection_name:str, id:int):
        col = Collection(collection_name)
        return col.query(expr=f"patent_id == {id}", output_fields=["id","patent_id","paragraph","title","abstract"], limit=1)