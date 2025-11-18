"""
Herramienta para eliminar un corpus RAG de Vertex AI cuando ya no se necesita.
"""

from google.adk.tools import ToolContext, FunctionTool
from vertexai import rag

from tools.utils import check_corpus_exists, get_corpus_resource_name

DESCRIPTION = "Elimina un corpus RAG de Vertex AI cuando ya no se necesita. Requiere confirmación para evitar eliminaciones accidentales."
SCHEMA = {
    "type": "object",
    "properties": {
        "corpus_name": {
            "type": "string",
            "description": "El nombre completo del recurso del corpus a eliminar. Preferiblemente use el resource_name de los resultados de list_corpora."
        },
        "confirm": {
            "type": "boolean",
            "description": "Debe establecerse en True para confirmar la eliminación"
        }
    },
}

def delete_corpus(
    corpus_name: str,
    confirm: bool,
    tool_context: ToolContext,
) -> dict:
    """
    Elimina un corpus RAG de Vertex AI cuando ya no se necesita.
    Requiere confirmación para evitar eliminaciones accidentales.

    Args:
        corpus_name (str): El nombre completo del recurso del corpus a eliminar.
                            Preferiblemente use el resource_name de los resultados de list_corpora.
        confirm (bool): Debe establecerse en True para confirmar la eliminación, si no se proporciona la confirmación pregunta.
        tool_context (ToolContext): El contexto de la herramienta
    Returns:
        dict: Información sobre el estado de la operación de eliminación
    """
    
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"El corpus '{corpus_name}' no existe",
            "corpus_name": corpus_name,
        }

    if not confirm:
        return {
            "status": "error",
            "message": "La eliminación requiere confirmación explícita. Establezca confirm=True para eliminar este corpus.",
            "corpus_name": corpus_name,
        }

    try:
   
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        rag.delete_corpus(corpus_resource_name)

        state_key = f"corpus_exists_{corpus_name}"
        if state_key in tool_context.state:
            tool_context.state[state_key] = False

        return {
            "status": "success",
            "message": f"Corpus '{corpus_name}' eliminado exitosamente",
            "corpus_name": corpus_name,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al borrar corpus: {str(e)}",
            "corpus_name": corpus_name,
        }
    
run = FunctionTool(func=delete_corpus)