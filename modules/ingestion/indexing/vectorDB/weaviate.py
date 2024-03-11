from modules.ingestion.embedding import huggingface
import weaviate
import json


class VectorDB:

    def __init__(self, 
                 weaviate_url: str, 
                 weaviate_api_key: str,
                 model_embedding: str 
                 ):
        
        super().__init__()

        self.WEAVIATE_URL = weaviate_url
        self.WEAVIATE_API_KEY = weaviate_api_key
        self.hf_embedder = huggingface.Embedder(model_url=model_embedding)
        
        self.client = weaviate.Client(
        url = self.WEAVIATE_URL,
        auth_client_secret=weaviate.auth.AuthApiKey(self.WEAVIATE_API_KEY)
    )
        
        
    def create_data_collection(self, class_name: str):

        if self.client.schema.exists(class_name):
            self.client.schema.delete_class(class_name)

        class_obj = {
            "class": class_name,
            "vectorizer": "none"
        }

        self.client.schema.create_class(class_obj)

    def add_data_to_collection(self, documents, class_name, batch_size: int=100):
        
        self.client.batch.configure(batch_size=batch_size)  

        with self.client.batch as batch:  # Initialize a batch process

            for i, doc in enumerate(documents):  # Batch import data

                properties = {
                    "tag": doc["tag"],
                    "level": doc["level"],
                    "page_idx": doc["page_idx"],
                    "file_name": doc["filename"],
                    "text": doc["text"],
                    "html_text": doc["html_text"]
                }
                batch.add_data_object(
                    data_object=properties,
                    class_name=class_name,
                    vector=doc['vector']
                )
    
    def retrieve_document(self, query_text: str, class_name: str, top_n: int=3):

        query_vector = self.hf_embedder.embedding_query(query_text)

        response = (
            self.client.query
            .get(class_name, ["page_idx", "text", "html_text"])
            .with_hybrid(
                query=query_text,
                vector=query_vector[0],
                alpha=0.8,
            )
            .with_additional("score")
            .with_limit(top_n)
            .do()
        )
        
        return response['data']['Get']

        

