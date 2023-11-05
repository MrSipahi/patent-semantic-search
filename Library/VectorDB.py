from Driver.MilvusDB import MilvusDB


class VectorDatabaseProvider:
    def __init__(self) -> None:
        self.vectorDB= MilvusDB()

    def search(self, collection_name:str,search_params:dict):
        return self.vectorDB.search(collection_name,search_params)

    def insert(self,collection_name:str, entities:list)->bool:
        return self.vectorDB.insert(collection_name, entities)

    def get(self, collection_name:str, id:int):
        return self.vectorDB.get(collection_name, id)