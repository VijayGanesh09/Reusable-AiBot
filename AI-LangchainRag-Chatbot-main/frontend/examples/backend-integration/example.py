import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
backend_path = project_root / "backend"

sys.path.insert(0, str(backend_path))

from rag_engine import RAGEngine

bot = RAGEngine()

answer = bot.chat("Explain the main points in my document")

print(answer)