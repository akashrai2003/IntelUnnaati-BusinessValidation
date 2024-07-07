import os
import traceback
from typing import Any, Dict, List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
# import google
import google.generativeai as genai
import pathlib
import textwrap
from IPython.display import Markdown
import PIL.Image
import logging
import time
from langchain_community.chat_models import AzureChatOpenAI


from dotenv import load_dotenv
load_dotenv()

AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_KEY=os.getenv("AZURE_OPENAI_API_KEY")
AZURE_VERSION=os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_TYPE=os.getenv("AZURE_OPENAI_API_TYPE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Configure the Generative AI client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-pro-vision')


def load_img(
    file_path: str,
    chunk_size: int, 
    chunk_overlap: int, 
    metadata_obj: Dict = None,
) -> List[Document]:    
    '''
    Load an image file and split its content into chunks of text.

    '''

    print("Loading Image")
    img_path = pathlib.Path(file_path)
    img = PIL.Image.open(img_path)
    prompt_template = '''
    Read all the text that you can from the given image. If the image contains handwritten text, carefully read and transcribe all the text, ensuring accuracy despite the challenging handwriting. If the image includes printed text, read and transcribe the text as accurately as possible. If the image contains a combination of handwritten and printed text, read and transcribe all the text, ensuring accuracy in both cases. Please proceed with the transcription.
    '''
    # Generate content from the image
    response = model.generate_content([prompt_template, img], stream=True)
    logging.info(f"prompt feedback: {response.prompt_feedback}")
    response.resolve()
    text = response.text
    logging.info(f"Text from image: {text}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)

    docs = [Document(chunk) for chunk in chunks]
    if metadata_obj:
        for doc in docs:
            doc.metadata["source"] = file_path.split("/")[-1]
            doc.metadata.update(metadata_obj)

    return docs

