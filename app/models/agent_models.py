from typing import Optional
from pydantic import BaseModel

class AgentRequest(BaseModel):
    question: str
    user_id: str
    session_id: Optional[str] = None
    train_memory: bool = False


class AgentResponse(BaseModel):
    response: str
