"""
Herramienta para recuperar información detallada sobre un corpus RAG específico.
"""

from google.adk.tools import ToolContext, FunctionTool
from vertexai import rag

from tools.utils import check_corpus_exists, get_corpus_resource_name

DESCRIPTION = "Obtiene información detallada sobre un corpus RAG específico, incluidos sus archivos."

SCHEMA = {
    "type": "object",
    "properties": {
        "corpus_name": {
            "type": "string",
            "description": "El nombre completo del recurso del corpus sobre el que se desea obtener información.",
        }
    },
    "required": ["corpus_name"],
}

def get_corpus_info(
    corpus_name: str,
    tool_context: ToolContext,
) -> dict:
    """
    Obtiene información detallada sobre un corpus RAG específico, incluidos sus archivos.
    Args:
        corpus_name (str): El nombre completo del recurso del corpus sobre el que se desea obtener información.
                           Preferiblemente use el resource_name de los resultados de list_corpora.
        tool_context (ToolContext): El contexto de la herramienta
    
    Returns:
        dict: Información sobre el corpus y sus archivos
    """
    try:
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"El corpus '{corpus_name}' no existe",
                "corpus_name": corpus_name,
            }

        corpus_resource_name = get_corpus_resource_name(corpus_name)

        corpus_display_name = corpus_name

        file_details = []
        try:
            files = rag.list_files(corpus_resource_name)
            for rag_file in files:
                try:
                    file_id = rag_file.name.split("/")[-1]

                    file_info = {
                        "file_id": file_id,
                        "display_name": (
                            rag_file.display_name
                            if hasattr(rag_file, "display_name")
                            else ""
                        ),
                        "source_uri": (
                            rag_file.source_uri
                            if hasattr(rag_file, "source_uri")
                            else ""
                        ),
                        "create_time": (
                            str(rag_file.create_time)
                            if hasattr(rag_file, "create_time")
                            else ""
                        ),
                        "update_time": (
                            str(rag_file.update_time)
                            if hasattr(rag_file, "update_time")
                            else ""
                        ),
                    }

                    file_details.append(file_info)
                except Exception:
                    continue
        except Exception:
            pass

        return {
            "status": "success",
            "message": f"Se obtuvo información para el corpus '{corpus_display_name}'",
            "corpus_name": corpus_name,
            "corpus_display_name": corpus_display_name,
            "file_count": len(file_details),
            "files": file_details,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener la información del corpus: {str(e)}",
            "corpus_name": corpus_name,
        }
    
run = FunctionTool(func=get_corpus_info)