from tqdm import tqdm
from wasabi import msg
from weaviate import Client

import torch
from torch.utils.data import DataLoader
from transformers import AutoModel, AutoTokenizer, DataCollatorWithPadding
from .dataset import ChunkDataset




class Embedder():

    def __init__(self):
        super().__init__()
        self.model_url = "sentence-transformers/all-MiniLM-L6-v2"
        self.model = None
        self.tokenizer = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

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

    def embedding(
        self,
        batch_size: int = 32,
        data_json: list[dict]
    ) -> bool:
        
        documents = [doc['text'] for doc in data]

        tokenized_data = self.tokenizer(documents, max_length=256, truncation=True)

        dataset = ChunkDataset(tokenized_data)

        dataloader = DataLoader(dataset,
                                batch_size=batch_size,
                                shuffle=False,
                                collate_fn=DataCollatorWithPadding(self.tokenizer))
        
        for batch in dataloader:

            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)

            output = self.model(input_ids, attention_mask)


