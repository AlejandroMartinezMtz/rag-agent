"""
Herramienta para crear un nuevo corpus RAG de Vertex AI.
"""

import re
from mcp import types as mcp_types
from vertexai import rag
from google.adk.tools import ToolContext, FunctionTool

from config import (
  DEFAULT_EMBEDDING_MODEL,
)

from tools.utils import check_corpus_exists

DESCRIPTION = "Crea un nuevo corpus RAG de Vertex AI con el nombre especificado."
SCHEMA = {
    "type": "object",
    "properties": {
        "corpus_name": {
            "type": "string",
            "description": "El nombre para el nuevo corpus"
        }
    },
}

def create_corpus(
    corpus_name: str,
    tool_context: ToolContext
) -> dict:
    """
    Crea un nuevo corpus RAG de Vertex AI con el nombre especificado.

    Args:
        corpus_name (str): El nombre para el nuevo corpus
        tool_context (ToolContext): El contexto de la herramienta para la gestión del estado

    Returns:
        dict: Información sobre el estado de la operación
    """

    if check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "info",
            "message": f"El corpus '{corpus_name}' ya existe",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }

    try:
       
        display_name = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_name)

        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model=DEFAULT_EMBEDDING_MODEL
            )
        )
        
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )

        tool_context.state[f"corpus_exists_{corpus_name}"] = True

        tool_context.state["current_corpus"] = corpus_name

        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' creado exitosamente",
            "corpus_name": rag_corpus.name,
            "display_name": rag_corpus.display_name,
            "corpus_created": True,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al crear el corpus: {str(e)}",
            "corpus_name": corpus_name,
            "corpus_created": False,
        }

run = FunctionTool(func=create_corpus)