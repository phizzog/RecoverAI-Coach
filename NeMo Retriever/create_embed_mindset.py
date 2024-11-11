import os
from dotenv import load_dotenv
from pymongo import MongoClient
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import StorageContext
from llama_index.core.base.embeddings.base import BaseEmbedding
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Optional
from pydantic import PrivateAttr

class CustomNVEmbedding(BaseEmbedding):
    model_name: str
    embed_batch_size: int = 2

    _model: Optional[SentenceTransformer] = PrivateAttr(default=None)
    _query_prefix: str = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self._load_model()

    def _load_model(self):
        self._model = SentenceTransformer(self.model_name, trust_remote_code=True)
        self._model.max_seq_length = 32768
        self._model.tokenizer.padding_side = "right"
        instruction = "Given a question, retrieve passages that answer the question"
        self._query_prefix = f"Instruct: {instruction}\nQuery: "

    def _add_eos(self, input_examples: List[str]) -> List[str]:
        eos_token = self._model.tokenizer.eos_token
        return [example + eos_token for example in input_examples]

    def _get_query_embedding(self, query: str) -> List[float]:
        return self.embed_function([query], is_query=True)[0].tolist()

    def _get_text_embedding(self, text: str) -> List[float]:
        return self.embed_function([text], is_query=False)[0].tolist()

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.embed_function(texts, is_query=False).tolist()

    # Async methods implementation...

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._get_text_embeddings(texts)

    def embed_function(self, texts: List[str], is_query: bool) -> np.ndarray:
        texts_with_eos = self._add_eos(texts)
        if is_query:
            embeddings = self._model.encode(
                texts_with_eos,
                batch_size=self.embed_batch_size,
                prompt=self._query_prefix,
                normalize_embeddings=True,
            )
        else:
            embeddings = self._model.encode(
                texts_with_eos,
                batch_size=self.embed_batch_size,
                normalize_embeddings=True,
            )
        return np.array(embeddings)

# Load environment variables from .env file
load_dotenv()

# MongoDB connection details
uri = os.environ.get('MONGODB_ATLAS_URI_MINDSET')
db_name = "docs"
collection_name = "embeddings"

# Create a MongoDB client
mongodb_client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)

# Initialize the MongoDB Atlas vector store
vector_store = MongoDBAtlasVectorSearch(
    mongodb_client=mongodb_client,
    db_name=db_name,
    collection_name=collection_name,
    vector_index_name="default",
    embedding_dimension=4096,
)

# Create a storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Define the directory path
docs_dir = "upload"

# Load NV-Embed-v2 model
model_name = "nvidia/NV-Embed-v2"
embed_model = CustomNVEmbedding(model_name=model_name, embed_batch_size=2)

# Process files one by one using SimpleDirectoryReader
for filename in os.listdir(docs_dir):
    file_path = os.path.join(docs_dir, filename)
    if os.path.isfile(file_path):
        print(f"Processing file: {filename}")
        
        # Use SimpleDirectoryReader to load a single file
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        # Create an index for this document
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=embed_model,
        )
        
        print(f"Indexed file: {filename}")

print("Indexing complete. All documents have been processed and stored in MongoDB Atlas.")
print("Please ensure you have created the appropriate Atlas Search index in your MongoDB Atlas cluster.")
