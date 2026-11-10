
import hashlib
import threading
import time

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.config import KNOWLEDGE_BASE_FOLDER
from app.ingestion import load_and_split_pdf, SUPPORTED_EXTENSIONS

from app.vectorstore import (
    get_vector_store,
    get_document_hashes,
    create_vector_store,
    delete_old_document_embeddings,
    delete_document_embeddings
)


# ==========================================
# SHARED PROCESSING LOCK
# ==========================================

PROCESSING_LOCK = threading.Lock()


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
# WAIT UNTIL FILE COPYING IS COMPLETE
# ==========================================

def wait_for_file_ready(file_path, attempts=10):

    previous_size = -1
    stable_count = 0

    for _ in range(attempts):

        try:

            if not file_path.exists():
                return False

            current_size = file_path.stat().st_size

            if current_size == previous_size and current_size > 0:
                stable_count += 1
            else:
                stable_count = 0

            if stable_count >= 2:
                return True

            previous_size = current_size

        except OSError:
            pass

        time.sleep(1)

    return False


# ==========================================
# PROCESS NEW OR MODIFIED DOCUMENT
# ==========================================

def process_document(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        return

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return

    with PROCESSING_LOCK:

        try:

            if not wait_for_file_ready(file_path):
                print(f"File is not ready: {file_path.name}")
                return

            if not file_path.exists():
                return

            relative_source = str(
                file_path.relative_to(Path(KNOWLEDGE_BASE_FOLDER))
            ).replace("\\", "/")

            current_hash = calculate_file_hash(file_path)

            vectorstore = get_vector_store()

            existing_hashes = get_document_hashes(
                vectorstore,
                relative_source
            )

            # Skip unchanged documents.
            if current_hash in existing_hashes:

                print(f"Unchanged document skipped: {relative_source}")
                return

            print("\n====================================")
            print(f"Processing document: {relative_source}")
            print("====================================")

            # Extract and split document into chunks.
            chunks = list(
                load_and_split_pdf(
                    file_path,
                    relative_source,
                    current_hash
                )
            )

            if not chunks:

                print(f"No text extracted: {relative_source}")
                return

            print(f"Total chunks extracted: {len(chunks)}")

            # Generate and store embeddings in batches.
            updated_vectorstore = create_vector_store(
                chunks,
                batch_size=32
            )

            # Delete only old versions after successful embedding.
            delete_old_document_embeddings(
                updated_vectorstore,
                relative_source,
                current_hash
            )

            print(f"Document updated successfully: {relative_source}")

        except Exception as error:

            print(f"Error processing document: {error}")


# ==========================================
# REMOVE DELETED DOCUMENT
# ==========================================

def remove_document(file_path):

    file_path = Path(file_path)

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return

    with PROCESSING_LOCK:

        try:

            relative_source = str(
                file_path.relative_to(Path(KNOWLEDGE_BASE_FOLDER))
            ).replace("\\", "/")

            vectorstore = get_vector_store()

            delete_document_embeddings(
                vectorstore,
                relative_source
            )

            print(f"Document removed: {relative_source}")

        except Exception as error:

            print(f"Error removing document: {error}")


# ==========================================
# WATCHDOG EVENT HANDLER
# ==========================================

class KnowledgeBaseHandler(FileSystemEventHandler):

    def __init__(self):

        self.timers = {}
        self.lock = threading.Lock()

    def cancel_pending_timer(self, file_path):

        key = str(Path(file_path))

        with self.lock:

            previous_timer = self.timers.pop(key, None)

            if previous_timer:
                previous_timer.cancel()

    def schedule_processing(self, file_path):

        file_path = Path(file_path)

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return

        key = str(file_path)

        with self.lock:

            previous_timer = self.timers.get(key)

            if previous_timer:
                previous_timer.cancel()

            timer = threading.Timer(
                2.0,
                self.process_after_delay,
                args=[file_path]
            )

            timer.daemon = True

            self.timers[key] = timer

            timer.start()

    def process_after_delay(self, file_path):

        key = str(file_path)

        with self.lock:
            self.timers.pop(key, None)

        if file_path.exists():
            process_document(file_path)

    def on_created(self, event):

        if not event.is_directory:
            self.schedule_processing(event.src_path)

    def on_modified(self, event):

        if not event.is_directory:
            self.schedule_processing(event.src_path)

    def on_deleted(self, event):

        self.cancel_pending_timer(event.src_path)

        if not event.is_directory:
            remove_document(event.src_path)

    def on_moved(self, event):

        if event.is_directory:
            return

        self.cancel_pending_timer(event.src_path)

        remove_document(event.src_path)

        self.schedule_processing(event.dest_path)


# ==========================================
# START FOLDER MONITOR
# ==========================================

def start_knowledge_monitor():

    folder = Path(KNOWLEDGE_BASE_FOLDER)

    folder.mkdir(parents=True, exist_ok=True)

    event_handler = KnowledgeBaseHandler()

    observer = Observer()

    observer.schedule(
        event_handler,
        str(folder),
        recursive=True
    )

    observer.start()

    print("\nKnowledge base folder monitoring started.")
    print(f"Monitoring folder: {folder}")

    return observer
