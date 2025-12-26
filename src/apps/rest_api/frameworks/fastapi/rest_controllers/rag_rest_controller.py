from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.core.container.container import Container
from src.core.features.rag.rag_controller import RagController

router = APIRouter(prefix="/rag", tags=["RAG"])

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
@inject
def rag_query(
    request: QueryRequest,
    controller: RagController = Depends(Provide[Container.rag_controller])
):
    return controller.query(request.query)
