
import os
import hashlib

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from app.config import KNOWLEDGE_BASE_FOLDER
from app.ingestion import load_and_split_pdf, SUPPORTED_EXTENSIONS

from app.vectorstore import (
    get_vector_store,
    create_vector_store,
    delete_old_document_embeddings
)

from app.rag_chain import generate_answer

from app.knowledge_monitor import (
    start_knowledge_monitor,
    PROCESSING_LOCK
)


# ==========================================
# FLASK INITIALIZATION
# ==========================================

app = Flask(__name__)
CORS(app)

WIDGET_FOLDER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend",
        "dist-widget"
    )
)

chatbot_ready = False
startup_error = None


# ==========================================
# FILE HASH
# ==========================================

def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for block in iter(lambda: file.read(4096), b""):
            sha256.update(block)

    return sha256.hexdigest()


# ==========================================
# GET EXISTING DOCUMENTS
# ==========================================

def get_existing_documents(vectorstore, source):

    return vectorstore.get(
        where={
            "$and": [
                {"source": source},
                {"knowledge_base": True}
            ]
        },
        include=["metadatas"]
    )


# ==========================================
# INITIAL KNOWLEDGE BASE SYNCHRONIZATION
# ==========================================

def process_knowledge_base():

    global chatbot_ready, startup_error

    # Prevent simultaneous processing by Watchdog.
    with PROCESSING_LOCK:

        chatbot_ready = False
        startup_error = None

        print("\n========== KNOWLEDGE BASE PROCESSING ==========")

        os.makedirs(KNOWLEDGE_BASE_FOLDER, exist_ok=True)

        vectorstore = get_vector_store()

        supported_files = []

        for root, dirs, files in os.walk(KNOWLEDGE_BASE_FOLDER):

            for filename in files:

                extension = os.path.splitext(filename)[1].lower()

                if extension in SUPPORTED_EXTENSIONS:
                    supported_files.append(
                        os.path.join(root, filename)
                    )

        current_sources = set()
        failed_files = []

        print("Files found:", len(supported_files))

        # ======================================
        # PROCESS NEW AND MODIFIED DOCUMENTS
        # ======================================

        for file_path in supported_files:

            relative_source = os.path.relpath(
                file_path,
                KNOWLEDGE_BASE_FOLDER
            ).replace("\\", "/")

            current_sources.add(relative_source)

            try:

                file_hash = calculate_file_hash(file_path)

                existing = get_existing_documents(
                    vectorstore,
                    relative_source
                )

                existing_hashes = {
                    metadata.get("file_hash")
                    for metadata in existing["metadatas"]
                    if metadata
                }

                # Skip unchanged documents.
                if file_hash in existing_hashes:

                    print(f"Unchanged - skipped: {relative_source}")
                    continue

                print("\n====================================")
                print(f"Processing: {relative_source}")
                print("====================================")

                # Extract and split document.
                chunks = list(
                    load_and_split_pdf(
                        file_path,
                        relative_source,
                        file_hash
                    )
                )

                if not chunks:

                    print(
                        f"No readable content - skipped: {relative_source}"
                    )

                    continue

                print(f"Total chunks extracted: {len(chunks)}")

                # Generate and store embeddings in batches of 32.
                updated_vectorstore = create_vector_store(
                    chunks,
                    batch_size=32
                )

                # Remove only previous versions.
                delete_old_document_embeddings(
                    updated_vectorstore,
                    relative_source,
                    file_hash
                )

                print(
                    f"Indexed successfully: {relative_source} "
                    f"({len(chunks)} chunks)"
                )

            except Exception as error:

                print(f"Error processing {relative_source}: {error}")

                failed_files.append(relative_source)

        # ======================================
        # REMOVE DELETED DOCUMENTS
        # ======================================

        existing_knowledge_base = vectorstore.get(
            where={"knowledge_base": True},
            include=["metadatas"]
        )

        deleted_ids = []

        for doc_id, metadata in zip(
            existing_knowledge_base["ids"],
            existing_knowledge_base["metadatas"]
        ):

            source = metadata.get("source")

            if source not in current_sources:
                deleted_ids.append(doc_id)

        if deleted_ids:

            vectorstore.delete(ids=deleted_ids)

            print(
                "Removed embeddings for deleted files:",
                len(deleted_ids)
            )

        # ======================================
        # FINAL STATUS
        # ======================================

        if failed_files:

            startup_error = (
                "Some knowledge-base files could not be processed: "
                + ", ".join(failed_files)
            )

            print(startup_error)
            print("Chat is not ready. Fix the errors and restart.")

        else:

            chatbot_ready = True

            print("\nKnowledge base is ready!")
            print("Total supported files:", len(supported_files))

        print("===============================================\n")


# ==========================================
# CHAT API
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    if not chatbot_ready:

        return jsonify({
            "error": startup_error or "Knowledge base is still initializing."
        }), 503

    data = request.get_json(silent=True) or {}

    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not question:

        return jsonify({
            "error": "Please enter a question."
        }), 400

    try:

        result = generate_answer(
            question,
            None,
            history
        )

        return jsonify(result)

    except Exception as error:

        print("Chat error:", str(error))

        return jsonify({
            "error": "Unable to generate an answer."
        }), 500


# ==========================================
# BACKEND STATUS
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "AI RAG Chatbot Backend",
        "ready": chatbot_ready,
        "error": startup_error
    })


# ==========================================
# WIDGET FILES
# ==========================================

@app.route("/widget.js", methods=["GET"])
def serve_widget():

    return send_from_directory(WIDGET_FOLDER, "widget.js")


@app.route("/widget.css", methods=["GET"])
def serve_widget_css():

    return send_from_directory(WIDGET_FOLDER, "widget.css")


# ==========================================
# START BACKEND
# ==========================================

if __name__ == "__main__":

    observer = None

    try:

        # First synchronize existing documents.
        process_knowledge_base()

        # Start automatic folder monitoring.
        observer = start_knowledge_monitor()

        app.run(
            debug=True,
            host="127.0.0.1",
            port=5000,
            use_reloader=False
        )

    finally:

        if observer:

            observer.stop()
            observer.join()
