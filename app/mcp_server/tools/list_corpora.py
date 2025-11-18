"""
Herramienta para listar todos los corpus RAG disponibles de Vertex AI.
"""

from typing import Dict, List, Union
from vertexai import rag
from google.adk.tools import ToolContext, FunctionTool

DESCRIPTION = "Lista todos los corpus RAG disponibles en Vertex AI"
SCHEMA = {
    "type": "object",
    "properties": {},
    "required": []
}

def list_corpora(tool_context: ToolContext = None) -> dict:
    """
    Lista todos los corpus RAG disponibles de Vertex AI.

    Returns:
        dict: Una lista de los corpus disponibles y el estado, con cada corpus que contiene:
            - resource_name: El nombre completo del recurso para usar con otras herramientas
            - display_name: El nombre legible del corpus
            - create_time: Cuando se creó el corpus
            - update_time: Cuando se actualizó por última vez el corpus
    """
    try:
        corpora = rag.list_corpora()

        corpus_info: List[Dict[str, Union[str, int]]] = []
        for corpus in corpora:
            corpus_data: Dict[str, Union[str, int]] = {
                "resource_name": corpus.name,
                "display_name": corpus.display_name,
                "create_time": (
                    str(corpus.create_time) if hasattr(corpus, "create_time") else ""
                ),
                "update_time": (
                    str(corpus.update_time) if hasattr(corpus, "update_time") else ""
                ),
            }
            corpus_info.append(corpus_data)

        if corpus_info:
            corpus_list = []
            for idx, corpus in enumerate(corpus_info, 1):
                info = f"{idx}. {corpus['display_name']}"
                info += f"\n   Resource Name: {corpus['resource_name']}"
                if corpus['create_time']:
                    info += f"\n   Creado: {corpus['create_time']}"
                corpus_list.append(info)
            
            corpus_texto = "\n\n".join(corpus_list)
            message = (
                f"Corpus RAG disponibles ({len(corpus_info)}):\n\n"
                f"{corpus_texto}\n\n"
                f"Puedes usar la herramienta 'get_corpus_info' para ver detalles de un corpus especifico."
            )
        else:
            message = "No se encontraron corpus RAG disponibles."

        return {
            "status": "success",
            "message": message,
            "corpora": corpus_info,
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al listar los corpus: {str(e)}",
            "corpora": [],
        }

run = FunctionTool(func=list_corpora)