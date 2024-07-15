from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
import os
import traceback
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
import numpy as np
from openai import AsyncOpenAI
from typing import Dict, List, Optional
import aiofiles
from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException, Request
import json
from data_loaders import load_documents
from upload import save_data
from utils.labels import find_labels
import logging
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
logging.basicConfig(level=logging.INFO)

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
hf_inference_api_key=os.getenv("HF_INFERENCE_API_KEY")

import requests

API_URL = "https://api-inference.huggingface.co/models/jogoni/autotrain-cuad-document-type-2883884341"
headers = {"Authorization": "Bearer {hf_inference_api_key}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "I like you. I love you",
})


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5, openai_api_key=openai_api_key)
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(name=pinecone_index_name)
logging.info(index.describe_index_stats())


@app.post("/upload/files")
async def upload_files(
    files: List[UploadFile],
    metadata: Optional[str] = Form(...),
):
    total_docs = []
    save_dir = "datasets"
    os.makedirs(save_dir, exist_ok=True)

    for file in files:
        file_path = os.path.join(save_dir, file.filename)
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        await file.close()

        if not isinstance(metadata, dict):
            metadata = json.loads(metadata)
        logging.info(f"Uploading file: {file.filename}, metadata: {metadata}")
        docs = load_documents(
            file_name=file.filename,
            file_path=file_path,
            chunk_size=1000,
            metadata_obj=metadata,
        )
        total_docs.extend(docs)
    try:
        length = save_data(total_docs)
        return {"message": "Files uploaded successfully", "metadata": metadata}, 200
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Error uploading files,\n {traceback.format_exc()}")
        raise e
    
@app.post("/results")
async def get_results(
    input_dir: str = "user_files", 
    input_file: str = "user_document.txt"

):
    '''
    Get the results from the uploaded files.
    '''
    list_of_clauses = []
    file_path = os.path.join(input_dir, input_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    list_of_clauses = find_clauses(content)
    label_preds = find_labels(list_of_clauses)
    pdf = create_pdf(list_of_clauses, label_preds)
    return FileResponse(path=pdf_path, filename="results.pdf", media_type='application/pdf')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)