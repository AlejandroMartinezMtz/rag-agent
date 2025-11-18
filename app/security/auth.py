from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from config import settings

security = HTTPBearer()

async def verify_token(credentials=Depends(security)):
    if credentials.credentials != settings.AGENT_BEARER_TOKEN:
        raise HTTPException(401, "Token inválido")
    return True

# Agregar más configuraciones de seguridad