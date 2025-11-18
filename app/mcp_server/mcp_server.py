"""
Servidor MCP con FastAPI que expone herramientas RAG a través de Model Context Protocol.
"""
import os
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from mcp import types as mcp_types
from google.adk.tools import ToolContext
import uvicorn

from tools import TOOLS_MAP

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MCP_SERVER_TOKEN = os.getenv("MCP_SERVER_TOKEN")

security = HTTPBearer()

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

def validate_token(token: str) -> bool:
    if not MCP_SERVER_TOKEN:
        logger.error("MCP_SERVER_TOKEN no está configurado")
        return False
    return token == MCP_SERVER_TOKEN


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    if not validate_token(token):
        logger.warning(f"Token inválido recibido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

class ToolContextManager:
    def __init__(self):
        self._contexts: Dict[str, ToolContext] = {}
    
    def get_or_create(self, request_id: str = "default") -> ToolContext:
        if request_id not in self._contexts:
            try:
                self._contexts[request_id] = ToolContext()
            except TypeError:
                class SimpleContext:
                    def __init__(self):
                        self.state = {}
                self._contexts[request_id] = SimpleContext()
        
        context = self._contexts[request_id]
        if not hasattr(context, 'state'):
            context.state = {}
        
        return context

context_manager = ToolContextManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

async def list_mcp_tools() -> list[mcp_types.Tool]:
    """Expone al agente la lista de tools disponibles con schema y descripción"""
    return [
        mcp_types.Tool(
            name=name,
            description=module.DESCRIPTION,
            inputSchema=module.SCHEMA
        )
        for name, module in TOOLS_MAP.items()
    ]

async def call_mcp_tool(
    name: str, 
    arguments: dict, 
    tool_context: ToolContext
) -> list[mcp_types.Content]:
    
    if name not in TOOLS_MAP:
        raise ValueError(f"Herramienta '{name}' no encontrada")
    
    try:
        tool_module = TOOLS_MAP[name]
        func = tool_module.run.func

        result = func(**arguments, tool_context=tool_context)
        
        return [mcp_types.TextContent(type="text", text=str(result))]
    
    except Exception as e:
        logger.exception(f"Error ejecutando herramienta {name}: {str(e)}")
        raise

@app.post("/api/mcp")
async def mcp_entrypoint(
    mcp_request: MCPRequest,
    token: str = Depends(verify_token)
):
    """
    Endpoint MCP que delega al MCP server y sigue el protocolo JSON-RPC 2.0.
    """
    request_id = mcp_request.id
    method = mcp_request.method
    params = mcp_request.params or {}

    try:
        result_data = None

        if method == "initialize":
            result_data = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "rag-mcp-server",
                    "version": "1.0.0",
                    "framework": "FastAPI"
                }
            }

        elif method == "tools/list":
            tools = await list_mcp_tools()
            result_data = {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.inputSchema
                    }
                    for t in tools
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if not tool_name:
                raise ValueError("El parámetro 'name' es requerido para 'tools/call'")
            
            tool_context = context_manager.get_or_create(str(request_id))
            
            content_list = await call_mcp_tool(tool_name, arguments, tool_context)
            
            result_data = {
                "content": [
                    {"type": c.type, "text": c.text}
                    for c in content_list
                ]
            }

        elif method == "notifications/initialized":
            result_data = None

        else:
            return JSONResponse(
                status_code=404,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"                    }
                }
            )

        return MCPResponse(
            jsonrpc="2.0",
            id=request_id,
            result=result_data
        )

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Invalid params: {str(e)}"
                }
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True # Only for development
    )