"""
Rutas REST para interactuar con el agente vía HTTP.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.config import settings
from agent_runner import AgentRunner

router = APIRouter(prefix="/agent", tags=["Agent"])

class QueryInput(BaseModel):
    message: str
    session_id: str | None = None

def get_runner() -> AgentRunner:
    return AgentRunner(
        project_id=settings.GOOGLE_PROJECT,
        location=settings.GOOGLE_LOCATION,
    )

@router.post("/ask")
async def ask_agent(
    payload: QueryInput,
    runner_builder: AgentRunner = Depends(get_runner),
):
    """
    Envía un mensaje al agente.
    Maneja sesión, crea Runner y devuelve respuesta.
    """

    session_id = runner_builder.get_or_create_session(payload.session_id)

    runner = runner_builder.build(session_id)

    try:
        response = await runner.run(payload.message)
        return {
            "session_id": session_id,
            "response": response.text,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
def get_session(
    session_id: str,
    runner_builder: AgentRunner = Depends(get_runner),
):
    exists = runner_builder.session_service.exists(session_id)

    return {
        "session_id": session_id,
        "exists": exists,
    }
