import concurrent.futures
from typing import List, NamedTuple, Optional, cast

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger


class FileEncoding(NamedTuple):
    """File encoding as the NamedTuple."""

    encoding: Optional[str]
    """The encoding of the file."""
    confidence: float
    """The confidence of the encoding."""
    language: Optional[str]
    """The language of the file."""


def detect_file_encodings(file_name: str, timeout: int = 5) -> List[FileEncoding]:
    """Try to detect the file encoding.

    Returns a list of `FileEncoding` tuples with the detected encodings ordered
    by confidence.

    Args:
        file_name: The path to the file to detect the encoding for.
        timeout: The timeout in seconds for the encoding detection.
    """
    import chardet

    def read_and_detect(file_name: str) -> List[dict]:
        with open(file_name, "rb") as f:
            rawdata = f.read()
        return cast(List[dict], chardet.detect_all(rawdata))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(read_and_detect, file_name)
        try:
            encodings = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(
                f"Timeout reached while detecting encoding for {file_name}"
            )

    if all(encoding["encoding"] is None for encoding in encodings):
        raise RuntimeError(f"Could not detect encoding for {file_name}")
    return [FileEncoding(**enc) for enc in encodings if enc["encoding"] is not None]


def load_text(
    file_name: str,
    chunk_size: int,
    chunk_overlap: int,
    encoding: str = "r",
    metadata_obj: Optional[dict] = None,
) -> list:
    try:
        with open(file_name, "r") as f:
            text = f.read()
    except UnicodeDecodeError as e:
        detected_encodings = detect_file_encodings(file_name)
        for encoding in detected_encodings:
            logger.debug(f"Trying encoding: {encoding.encoding}")
            try:
                with open(file_name, encoding=encoding.encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue

    except Exception as e:
        logger.exception(f"Error loading file")
        raise RuntimeError(f"Error loading {file_name}") from e

    metadata = metadata_obj
    metadata.update({"source": file_name})
    documents = [Document(page_content=text, metadata=metadata)]

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    docs = text_splitter.split_documents(documents)
    return docs
