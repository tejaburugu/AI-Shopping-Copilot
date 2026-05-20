from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.rag import rag_service
from models.response import AskResponse
from models.db import UserTable
from services.auth_service import get_current_user

router = APIRouter()


class AskRequest(BaseModel):
    query: str
    session_id: str | None = None


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest, current_user: UserTable = Depends(get_current_user)):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    session_id = request.session_id or f"user:{current_user.id}"
    rag_response = await rag_service.answer_query(query, top_k=5, session_id=session_id)

    return AskResponse(
        query=query,
        contextual_query=rag_response["contextual_query"],
        answer=rag_response["answer"],
        structured_answer=rag_response["structured_answer"],
        context=rag_response["context"],
        previous_queries=rag_response["previous_queries"],
        products=rag_response["products"],
    )
