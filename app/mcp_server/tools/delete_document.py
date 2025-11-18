"""
Herramienta para eliminar un documento específico de un corpus RAG de Vertex AI.
"""

from google.adk.tools import ToolContext, FunctionTool
from vertexai import rag

from tools.utils import check_corpus_exists, get_corpus_resource_name


DESCRIPTION = "Elimina un documento específico de un corpus RAG de Vertex AI."
SCHEMA = {
    "type": "object",
    "properties": {
        "corpus_name": {
            "type": "string",
            "description": "El nombre completo del recurso del corpus que contiene el documento. Preferiblemente use el resource_name de los resultados de list_corpora."
        },
        "document_id": {
            "type": "string",
            "description": "El ID del documento/archivo específico a eliminar. Esto se puede obtener de los resultados de get_corpus_info."
        }
    },
    "required": ["corpus_name", "document_id"],
}

def delete_document(
    corpus_name: str,
    document_id: str,
    tool_context: ToolContext,
) -> dict:
    """
    Borra un documento específico de un corpus RAG de Vertex AI.

    Args:
        corpus_name (str): El nombre completo del recurso del corpus que contiene el documento.
                            Preferiblemente use el resource_name de los resultados de list_corpora.
        document_id (str): El ID del documento/archivo específico a eliminar. Esto se puede
                           obtener de los resultados de get_corpus_info.
        tool_context (ToolContext): El contexto de la herramienta

    Returns:
        dict: Información sobre el estado de la operación de eliminación
    """

    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"El corpus '{corpus_name}' no existe",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }

    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        rag_file_path = f"{corpus_resource_name}/ragFiles/{document_id}"
        rag.delete_file(rag_file_path)

        return {
            "status": "success",
            "message": f"Documento '{document_id}' eliminado exitosamente del corpus '{corpus_name}'",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al eliminar el documento: {str(e)}",
            "corpus_name": corpus_name,
            "document_id": document_id,
        }
    
run = FunctionTool(func=delete_document)