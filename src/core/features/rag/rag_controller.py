from .rag_service import RagService


class RagController:
    def __init__(self, rag_service: RagService):
        self.rag_service = rag_service

    async def query(self, user_query: str) -> dict:
        relevant_docs = await self.rag_service.retrieve(user_query)

        print("relevant_docs", relevant_docs)

        answer = self.rag_service.generate(relevant_docs, user_query)

        return {"query": user_query, "answer": answer, "retrieved_docs": relevant_docs}
