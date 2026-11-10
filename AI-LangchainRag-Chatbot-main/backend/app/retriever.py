
from app.vectorstore import get_vector_store
from app.config import TOP_K


# ==========================================
# RETRIEVE DOCUMENTS
# ==========================================

def retrieve_documents(question):

    if not question or not question.strip():
        return []

    vectorstore = get_vector_store()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": TOP_K
        }
    )

    documents = retriever.invoke(question.strip())

    return documents
