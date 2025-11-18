"""
Herramienta para consultar corpus RAG de Vertex AI y recuperar información relevante.
"""

from google.adk.tools import ToolContext, FunctionTool
from vertexai import rag

from config import (
    DEFAULT_DISTANCE_THRESHOLD,
    DEFAULT_TOP_K,
    CORPUS_NAME,
)
from .utils import check_corpus_exists, get_corpus_resource_name

DESCRIPTION = "Busca información en un corpus RAG. Puedes especificar el corpus en el query de forma natural."

SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": (
                "La pregunta o búsqueda que deseas hacer. Puedes mencionar el corpus específico "
                "en lenguaje natural (ej: 'en el corpus de trámites') o dejarlo para usar el corpus por defecto"
            ),
        },
        "corpus_name": {
            "type": "string",
            "description": (
                "Nombre específico del corpus donde buscar. Opcional: si no se proporciona, "
                "se usará el corpus por defecto o se intentará extraer del query"
            ),
        },
    },
    "required": ["query"],
}

def rag_query(
    query: str,
    tool_context: ToolContext,
    corpus_name: str = None,
) -> dict:
    """
    Consulta un corpus RAG de Vertex AI con una pregunta del usuario.
    
    El agente puede mencionar el corpus en lenguaje natural dentro del query:
    - "Busca requisitos de renovación de licencia en el corpus de trámites"
    - "¿Qué documentos necesito para mi acta de nacimiento?"
    
    Args:
        query (str): La consulta de texto. Puede incluir el nombre del corpus en lenguaje natural.
        tool_context (ToolContext, opcional): El contexto de la herramienta
        corpus_name (str, opcional): Nombre específico del corpus. Si no se proporciona, usa CORPUS_NAME por defecto.
    
    Returns:
        dict: Los resultados de la consulta y el estado
    """
    try:
        if not corpus_name:
            corpus_name = CORPUS_NAME
        
        if tool_context and not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"El corpus '{corpus_name}' no existe. Por favor créalo primero usando la herramienta create_corpus.",
                "query": query,
                "corpus_name": corpus_name,
            }

        corpus_resource_name = get_corpus_resource_name(corpus_name)

        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_resource_name,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": (
                        ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""
                    ),
                    "source_name": (
                        ctx_group.source_display_name
                        if hasattr(ctx_group, "source_display_name")
                        else ""
                    ),
                    "text": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)

        if not results:
            return {
                "status": "warning",
                "message": f"No se encontro información del corpus'{corpus_name}' para la consulta: '{query}'",
                "query": query,
                "corpus_name": corpus_name,
                "results": [],
                "results_count": 0,
            }

        return {
            "status": "success",
            "message": f"Se obtuvo la siguiente información del corpus '{corpus_name}' \n",
            "query": query,
            "corpus_name": corpus_name,
            "results": results,
            "results_count": len(results),
        }

    except Exception as e:
        error_msg = f"Error al consultar información: {str(e)}"
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
            "corpus_name": corpus_name,
        }
    
run = FunctionTool(func=rag_query)