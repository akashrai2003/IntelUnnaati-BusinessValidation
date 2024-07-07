from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
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
from upload import upload_data
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
    metadata: str = Form(...),
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

        docs = load_documents(
            file_name=file.filename,
            file_path=file_path,
            chunk_size=1000,
            metadata_obj=metadata,
        )
        total_docs.extend(docs)
    try:
        upload_data(total_docs)
        return {"message": "Files uploaded successfully", "metadata": metadata}, 200
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Error uploading files,\n {traceback.format_exc()}")
        raise e