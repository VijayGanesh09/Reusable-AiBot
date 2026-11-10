
import os
import uuid

from langchain_community.vectorstores import Chroma

from app.config import CHROMA_DB_PATH
from app.embeddings import get_embedding_model


# ==========================================
# CONFIGURATION
# ==========================================

COLLECTION_NAME = "rag_documents"
BATCH_SIZE = 32


# ==========================================
# GET VECTOR STORE
# ==========================================

def get_vector_store():

    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    embeddings = get_embedding_model()

    return Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )


# ==========================================
# GET EXISTING DOCUMENT HASHES
# ==========================================

def get_document_hashes(vectorstore, source):

    existing = vectorstore.get(
        where={
            "$and": [
                {"source": source},
                {"knowledge_base": True}
            ]
        },
        include=["metadatas"]
    )

    return {
        metadata.get("file_hash")
        for metadata in existing["metadatas"]
        if metadata
    }


# ==========================================
# CREATE AND STORE EMBEDDINGS
# ==========================================

def create_vector_store(chunks, batch_size=BATCH_SIZE):

    if not chunks:

        print("No chunks available for embedding.")
        return None

    vectorstore = get_vector_store()

    total_chunks = len(chunks)
    stored_count = 0

    print("\nGenerating and storing embeddings...")
    print(f"Total chunks: {total_chunks}")

    for start in range(0, total_chunks, batch_size):

        batch = chunks[start:start + batch_size]

        chunk_ids = [
            str(uuid.uuid4())
            for _ in batch
        ]

        vectorstore.add_documents(
            documents=batch,
            ids=chunk_ids
        )

        stored_count += len(batch)

        print(
            f"Embeddings stored: {stored_count} / {total_chunks}"
        )

    print(
        f"\nSuccessfully stored {stored_count} embeddings."
    )

    return vectorstore


# ==========================================
# DELETE OLD VERSIONS OF A DOCUMENT
# ==========================================

def delete_old_document_embeddings(
    vectorstore,
    source,
    current_hash
):

    existing = vectorstore.get(
        where={
            "$and": [
                {"source": source},
                {"knowledge_base": True}
            ]
        },
        include=["metadatas"]
    )

    old_ids = []

    for doc_id, metadata in zip(
        existing["ids"],
        existing["metadatas"]
    ):

        if metadata and metadata.get("file_hash") != current_hash:
            old_ids.append(doc_id)

    if old_ids:

        vectorstore.delete(ids=old_ids)

        print(
            f"Removed {len(old_ids)} old embeddings for: {source}"
        )


# ==========================================
# DELETE ALL EMBEDDINGS FOR A DOCUMENT
# ==========================================

def delete_document_embeddings(vectorstore, source):

    existing = vectorstore.get(
        where={
            "$and": [
                {"source": source},
                {"knowledge_base": True}
            ]
        }
    )

    if existing["ids"]:

        vectorstore.delete(ids=existing["ids"])

        print(
            f"Deleted {len(existing['ids'])} embeddings for: {source}"
        )
# ==========================================
# DELETE ALL EMBEDDINGS
# ==========================================

def delete_all_embeddings():

    vectorstore = get_vector_store()

    existing = vectorstore.get()

    all_ids = existing["ids"]

    if all_ids:
        vectorstore.delete(ids=all_ids)

        print(f"Deleted {len(all_ids)} embeddings from ChromaDB.")

    else:
        print("No embeddings found in ChromaDB.")