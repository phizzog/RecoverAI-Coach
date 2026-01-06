import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# MongoDB connection
uri = os.environ.get('MONGODB_ATLAS_URI_MINDSET')
tls_allow_invalid = os.environ.get('TLS_ALLOW_INVALID_CERTS', 'false').lower() == 'true'
client = MongoClient(uri, tls=True, tlsAllowInvalidCertificates=tls_allow_invalid)
db = client.docs
collection = db.embeddings

# NVIDIA API key
api_key = os.environ.get('NVIDIA_API_KEY')

# Create OpenAI client for NVIDIA API
openai_client = OpenAI(
    api_key=api_key,
    base_url="https://integrate.api.nvidia.com/v1"
)

# Initialize the tokenizer for token counting
tokenizer = tiktoken.get_encoding("cl100k_base")

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=[text],
        model="nvidia/nv-embed-v1",
        encoding_format="float",
        extra_body={"input_type": "query", "truncate": "NONE"}
    )
    return response.data[0].embedding

class Query(BaseModel):
    query_text: str

@app.post('/search')
async def search(query: Query):
    if not query.query_text:
        raise HTTPException(status_code=400, detail='query_text is required')
    
    query_embedding = get_embedding(query.query_text)
    
    results = collection.aggregate([
        {
            '$search': {
                'knnBeta': {
                    'path': 'embedding',
                    'vector': query_embedding,
                    'k': 20
                }
            }
        }
    ])

    result_texts = [result['text'] for result in results]
    print(result_texts)

    # Calculate token counts using the tokenizer
    token_counts = [len(tokenizer.encode(text)) for text in result_texts]
    total_tokens = sum(token_counts)
    print('Token count:', total_tokens)

    return JSONResponse(content=result_texts)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5003)