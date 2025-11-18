"""
Agente especializado en recuperar información sobre trámites gubernamentales.
"""

import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.genai import types
from dotenv import load_dotenv

from prompts.procedure_agent_prompt import PROCEDURE_AGENT_PROMPT

load_dotenv()

MCP_SERVER_TOKEN = os.getenv("MCP_SERVER_TOKEN")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
MODEL_GEMINI = os.getenv("MODEL_GEMINI")

def create_procedure_agent() -> Agent:
    """
    Crea el agente especializado en información sobre trámites.
    
    Returns:
        Agent: Agente configurado con herramientas MCP para consultas RAG en trámites.
    """
    headers = {
        "Authorization": f"Bearer {MCP_SERVER_TOKEN}"
    }

    return Agent(
        name="procedure_info_agent",
        model=MODEL_GEMINI,
        description="Agente especializado en recuperar información sobre trámites gubernamentales usando RAG.",
        instruction=PROCEDURE_AGENT_PROMPT,
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

procedure_agent = create_procedure_agent()