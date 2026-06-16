from fastapi import APIRouter
from app.schemas import AskIn

router = APIRouter(prefix="/model", tags=["model"])


@router.post("/ask")
def ask_model(payload: AskIn):
    # Placeholder answer - model integration to be added later
    return {"answer": f"(placeholder) We received your question in {payload.language}: {payload.question}", "confidence": 0.5}
