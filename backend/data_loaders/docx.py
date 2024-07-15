import concurrent.futures
from typing import List, NamedTuple, Optional, cast

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.word_document import Docx2txtLoader
from loguru import logger


def load_docx(
    file_name: str,
    chunk_size: int,
    chunk_overlap: int = 0,
    metadata_obj: Optional[dict] = None,
) -> list:
    """
    Load a Word document, extract the content, and split it into chunks of text.

    Args:
        file_name (str): The name of the Word document file.
        chunk_size (int): The size of each text chunk.
        chunk_overlap (int): The number of characters to overlap between consecutive chunks.

    Returns:
        List: A list of text chunks obtained from the Word document.
    """
    loader = Docx2txtLoader(file_name)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = text_splitter.split_documents(data)
    if metadata_obj:
        for doc in docs:
            doc.metadata["source"] = file_name.split("/")[-1]
            doc.metadata.update(metadata_obj)

    return docs
