import json
import httpx
from fastapi import APIRouter, HTTPException
from app.schemas import AskIn
from app.core.config import settings

router = APIRouter(prefix="/model", tags=["model"])

HF_SPACE_BASE = "https://dianepretty-wambaza-api.hf.space/gradio_api/call/answer"


@router.post("/ask")
def ask_model(payload: AskIn):
    try:
        with httpx.Client(timeout=120.0) as client:
            # Step 1: submit the question, get an event_id
            resp = client.post(
                HF_SPACE_BASE,
                json={"data": [payload.question]},
            )
            resp.raise_for_status()
            event_id = resp.json()["event_id"]

            # Step 2: poll the result stream until complete
            result_resp = client.get(f"{HF_SPACE_BASE}/{event_id}")
            result_resp.raise_for_status()

        # Parse SSE: wait for "event: complete" then read its "data: [...]" line
        answer = ""
        lines = result_resp.text.splitlines()
        for i, line in enumerate(lines):
            if line.strip() == "event: complete":
                for data_line in lines[i + 1:]:
                    if data_line.startswith("data:"):
                        parsed = json.loads(data_line[len("data:"):].strip())
                        if parsed and parsed[0]:
                            answer = parsed[0]
                        break
                break

        if not answer:
            raise HTTPException(status_code=502, detail="Empty response from model")

        words = len(answer.split())
        confidence = min(0.95, max(0.35, words / 100))

        return {"answer": answer, "confidence": round(confidence, 2)}

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Model request timed out")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
