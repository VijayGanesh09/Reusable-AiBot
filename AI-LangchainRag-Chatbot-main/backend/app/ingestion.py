
import os

from docx import Document as WordDocument

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_SIZE, CHUNK_OVERLAP


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def load_document(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        loader = PyPDFLoader(file_path)
        return loader.lazy_load()

    elif extension == ".docx":

        word_file = WordDocument(file_path)

        content = []

        for paragraph in word_file.paragraphs:

            if paragraph.text.strip():
                content.append(paragraph.text)

        for table in word_file.tables:

            for row in table.rows:

                row_text = " | ".join(
                    cell.text.strip() for cell in row.cells
                )

                if row_text.strip():
                    content.append(row_text)

        text = "\n".join(content)

    elif extension in {".txt", ".md"}:

        with open(file_path, "r", encoding="utf-8-sig") as file:
            text = file.read()

    else:

        raise ValueError(
            f"Unsupported file format: {extension}"
        )

    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={}
        )
    ]


def load_and_split_pdf(file_path, document_id, file_hash):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = os.path.splitext(file_path)[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            f"Unsupported file format: {extension}"
        )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )

    documents = load_document(file_path)

    for document in documents:

        if not document.page_content.strip():
            continue

        page_chunks = text_splitter.split_documents(
            [document]
        )

        for chunk in page_chunks:

            chunk.metadata["source"] = document_id
            chunk.metadata["document_id"] = document_id
            chunk.metadata["file_type"] = extension.lstrip(".")
            chunk.metadata["file_hash"] = file_hash
            chunk.metadata["knowledge_base"] = True

            yield chunk
