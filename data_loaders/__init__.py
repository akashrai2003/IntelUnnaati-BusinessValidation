import os
import traceback
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from loguru import logger

from .images import load_img
from .docx import load_docx
from .pdf import load_pdf
from .text import load_text


def load_documents(
    file_name: str,
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
    metadata_obj: Optional[Dict] = None,
) -> List[Document]:
    """
    Load documents based on the specified document type.

    Args:
        metadata_obj:
        file_path:
        file_name (str): The file_name to load the documents from.
        chunk_size (int, optional): The size of each text chunk. Defaults to 1000.
        chunk_overlap (int, optional): The number of characters to overlap between consecutive chunks. Defaults to 0.

    Returns:
        List[Document]: A list of loaded documents.

    Raises:
        ValueError: If an unsupported document type is provided.
    """

    try:
        docs = []
        if file_name.lower().endswith(".pdf"):
            docs = load_pdf(
                file_path, chunk_size, chunk_overlap, metadata_obj=metadata_obj
            )
        elif file_name.lower().endswith(".txt"):
            docs = load_text(
                file_path, chunk_size, chunk_overlap, metadata_obj=metadata_obj
            )
        elif file_name.lower().endswith(".docx"):
            docs = load_docx(
                file_path, chunk_size, chunk_overlap, metadata_obj=metadata_obj
            )
        elif file_name.lower().endswith(".csv"):
            docs = load_img(
                file_path, chunk_size, metadata_obj=metadata_obj
            )
        else:
            print("Unknown file format. not loading: ", file_name.lower())
        

        # try:
        #     os.remove(file_path)
        # except FileNotFoundError:
        #     print("Unable to delete file", file_path)

        return docs
    except Exception as e:
        raise e
