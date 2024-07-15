from typing import Dict, List, Optional

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFLoader
from loguru import logger


def load_pdf(
    file_name: str,
    chunk_size: int,
    chunk_overlap: int = 0,
    metadata_obj: Optional[Dict] = None,
) -> List[Document]:
    """
    Load a PDF file and split its content into chunks of text.

    Args:
        file_name (str): The name of the PDF file to load.
        chunk_size (int): The size of each text chunk.
        chunk_overlap (int): The overlap between consecutive text chunks.

    Returns:
        List: A list of text chunks obtained from the PDF file.
    """
    print("Loading PDF")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    try:
        loader = PyPDFLoader(file_name)
        data = loader.load()
        docs = text_splitter.split_documents(data)
        logger.info(f"Succesfully loaded and splitted file: {file_name}")
    except Exception as e2:
        raise e2  # Handle the case where all loaders fail
    if metadata_obj:
        for doc in docs:
            doc.metadata["source"] = file_name.split("/")[-1]
            doc.metadata.update(metadata_obj)

    return docs
