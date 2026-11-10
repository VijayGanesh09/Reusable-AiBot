from app.rag_chain import generate_answer


class RAGEngine:

    def chat(self, question, history=None):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        answer = generate_answer(
            question=question,
            chat_history=history or []
        )

        return answer