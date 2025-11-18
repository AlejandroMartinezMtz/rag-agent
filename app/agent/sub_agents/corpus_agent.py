"""
Agente especializado en (eliminar, crear, listar y obtener información) de corpus y (agregar y eliminar) documentos en el corpus RAG.

"""

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.genai import types
import os
from dotenv import load_dotenv

from prompts.corpus_agent_prompt import CORPUS_AGENT_PROMPT

load_dotenv()
MCP_SERVER_TOKEN = os.getenv("MCP_SERVER_TOKEN")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
MODEL_GEMINI = os.getenv("MODEL_GEMINI")

def create_corpus_agent() -> Agent:
    """
    Crea el agente especializado en crear e informar sobre corpus RAG.
    
    Returns:
        Agent: Agente configurado con herramientas MCP para gestionar corpus RAG y documentos.
    """
    headers = {
        "Authorization": f"Bearer {MCP_SERVER_TOKEN}"
    }

    return Agent(
        name="corpus_info_agent",
        model=MODEL_GEMINI,
        description="Agente especializado en crear corpus y recuperar información sobre corpus RAG en Vertex AI",
        instruction=CORPUS_AGENT_PROMPT,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=f"{MCP_SERVER_URL}/api/mcp",
                    headers=headers
                )
            )
        ],
        generate_content_config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=800,
            top_p=0.9,
        )
    )

corpus_agent = create_corpus_agent()