from tqdm import tqdm
from wasabi import msg
from weaviate import Client

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import AutoModel, AutoTokenizer, DataCollatorWithPadding
from .dataset import ChunkDataset
from typing import List

class Embedder:

    def __init__(self, model_url: str, batch_size: int=16):
        
        super().__init__()
        self.model_url = model_url
        self.model = None
        self.tokenizer = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.batch_size = batch_size

        try:

            self.model = AutoModel.from_pretrained(
                self.model_url , device_map=self.device
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_url , device_map=self.device
            )
            self.model = self.model.to(self.device)

        except Exception as e:
            msg.warn(str(e))
            pass
    
    def _tokenize_data(self, documents):

        list_text = [i['text'] for i in documents]

        tokenized_data = self.tokenizer(list_text, max_length=256, truncation=True)

        dataset = ChunkDataset(tokenized_data)
        
        dataloader = DataLoader(
                    dataset,
                    batch_size=self.batch_size,
                    shuffle=False,
                    collate_fn=DataCollatorWithPadding(self.tokenizer)
                )

        return dataloader       
    
    # Mean Pooling - Take attention mask into account for correct averaging
    # doc: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    def _mean_pooling(self, model_output, attention_mask):

        #First element of model_output contains all token embeddings
        token_embeddings = model_output[0] 
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    

    def embedding_documents(
        self,
        documents: list[dict],
    ) -> bool:

        try: 
            dataloader = self._tokenize_data(documents)

            for batch_index, batch in enumerate(dataloader):

                # Chage to compatible device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)

                model_output = self.model(input_ids, attention_mask)

                # Perform pooling and Normalize embeddings
                sentence_embeddings = self._mean_pooling(model_output, attention_mask)
                sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

                # Change to a list
                sentence_embeddings = sentence_embeddings.tolist()
                
                # Get a real index of each documents
                index = range( (self.batch_size*batch_index) , min((self.batch_size*batch_index+self.batch_size), len(documents)))
                
                for i, doc_index in enumerate(index):
                    documents[doc_index]['vector'] = sentence_embeddings[i]

            # Release GPU memory
            torch.cuda.empty_cache()

            return True

        except Exception as e:
            msg.warn(str(e))

            # Release GPU memory
            torch.cuda.empty_cache()

            return False
        
    
    def embedding_query(
            self,
            query: str
    ) -> List:
        
        tokenized_query = self.tokenizer([query], return_tensors='pt')
        tokenized_query.to(self.device)

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**tokenized_query)

        # Perform pooling and Normalize embeddings
        sentence_embeddings = self._mean_pooling(model_output, tokenized_query['attention_mask'])
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings.tolist()




    



