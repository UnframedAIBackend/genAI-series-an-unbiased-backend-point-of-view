from .rag_service import RagService

class RagController:
    def __init__(self, rag_service: RagService):
        self.rag_service = rag_service

    def query(self, user_query: str) -> dict:
        # 1. Retrieve
        relevant_docs = self.rag_service.retrieve(user_query)
        
        # 2. Generate
        answer = self.rag_service.generate(relevant_docs, user_query)
        
        return {
            "query": user_query,
            "answer": answer,
            "retrieved_docs": relevant_docs
        }
