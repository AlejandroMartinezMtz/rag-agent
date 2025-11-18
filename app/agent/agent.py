"""
Agente ADK que consume el servidor MCP Server.
"""
import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

from prompts.root_agent_prompt import ROOT_AGENT_PROMPT
from sub_agents.procedure_agent import procedure_agent
from sub_agents.corpus_agent import corpus_agent

load_dotenv()

MCP_SERVER_TOKEN = os.getenv("MCP_SERVER_TOKEN")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

MODEL_GEMINI = os.getenv("MODEL_GEMINI")

root_agent = LlmAgent(
    name="multi_domain_agent",
    model=MODEL_GEMINI,
    description=(
        "Agente orquestador que delega tareas a agentes especializados."       
    ),
    instruction=ROOT_AGENT_PROMPT,
    sub_agents=[procedure_agent, corpus_agent],
)