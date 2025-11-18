"""
Herramienta para agregar nuevas fuentes de datos a un corpus RAG de Vertex AI.
"""

from typing import List, Dict
from vertexai import rag
from google.adk.tools import ToolContext, FunctionTool

from config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
    CORPUS_NAME,
)
from tools.utils import check_corpus_exists, get_corpus_resource_name

DESCRIPTION = "Agrega nuevos documentos al corpus RAG desde rutas de Google Cloud Storage (gs://)"
SCHEMA = {
    "type": "object",
    "properties": {
        "corpus_name": {
            "type": "string",
            "description": "Nombre del corpus RAG",
        },
        "paths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lista de rutas GCS. Ejemplo: ['gs://bucket/archivo.pdf', 'gs://bucket/carpeta/']"
        }
    },
    "required": ["paths"]
}

def add_data(corpus_name: str, paths: List[str], tool_context: ToolContext) -> Dict:
    """
    Agregar nuevas fuentes de datos a un corpus RAG de Vertex AI.
    SOLO admite rutas GCS.
    
    Args:
        corpus_name (str): El nombre del corpus al que se agregará datos. Si no se proporciona, usa CORPUS_NAME por defecto.
        paths (List[str]): Lista de rutas GCS para agregar al corpus.
                          Ejemplo: ["gs://mi_bucket/mi_directorio_de_archivos", "gs://otro_bucket/archivo_individual.pdf"]
        tool_context (ToolContext): El contexto de la herramienta
        
    Returns:
        dict: Información sobre los datos agregados y el estado
    """

    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "error",
            "message": f"Corpus '{corpus_name}' no existe. Crealo primero.",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    if not paths or not all(isinstance(path, str) for path in paths):
        return {
            "status": "error",
            "message": "Rutas invalidas: Por favor proporciona una lista de rutas GCS (cadenas de texto).",
            "corpus_name": corpus_name,
            "paths": paths,
        }

    validated_paths = []
    invalid_paths = []

    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(f"{path} (no es un string valido)")
            continue

        if path.startswith("gs://"):
            validated_paths.append(path)
        else:
            invalid_paths.append(f"{path} (formato GCS invalido)")

    if not validated_paths:
        return {
            "status": "error",
            "message": "Ninguna ruta GCS valida proporcionada. Por favor, proporciona rutas que comiencen con 'gs://'.",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths,
        }

    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=DEFAULT_CHUNK_SIZE,
                chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            ),
        )

        import_result = rag.import_files(
            corpus_resource_name,
            validated_paths,
            transformation_config=transformation_config,
            max_embedding_requests_per_min=DEFAULT_EMBEDDING_REQUESTS_PER_MIN,
        )

        if not tool_context.state.get("current_corpus"):
            tool_context.state["current_corpus"] = corpus_name

        return {
            "status": "success",
            "message": f"Se agregaron exitosamente {import_result.imported_rag_files_count} archivo(s) al corpus '{corpus_name}'",
            "corpus_name": corpus_name,
            "files_added": import_result.imported_rag_files_count,
            "paths": validated_paths,
            "invalid_paths": invalid_paths,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al agregar documentos al corpus: {str(e)}",
            "corpus_name": corpus_name,
            "paths": paths,
        }

run = FunctionTool(func=add_data)