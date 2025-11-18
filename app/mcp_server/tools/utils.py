"""
Funciones utilitarias para las herramientas RAG.
"""

import logging
import re

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from config import (
    LOCATION,
    PROJECT_ID,
)

logger = logging.getLogger(__name__)

def get_corpus_resource_name(corpus_name: str) -> str:
    """
    Convierte un nombre de corpus a su nombre completo de recurso si es necesario.
    Maneja varios formatos de entrada y asegura que el nombre devuelto siga los requisitos de Vertex AI.

    Args:
        corpus_name (str): El nombre del corpus o el nombre para mostrar
    
    Returns:
        str: El nombre completo del recurso del corpus
    """

    if re.match(r"^projects/[^/]+/locations/[^/]+/ragCorpora/[^/]+$", corpus_name):
        return corpus_name

    try:
        corpora = rag.list_corpora()
        for corpus in corpora:
            if hasattr(corpus, "display_name") and corpus.display_name == corpus_name:
                return corpus.name
    except Exception as e:
        logger.warning(f"Error cuando se verifica el nombre para mostrar del corpus: {str(e)}")
        pass

    if "/" in corpus_name:
        corpus_id = corpus_name.split("/")[-1]
    else:
        corpus_id = corpus_name

    corpus_id = re.sub(r"[^a-zA-Z0-9_-]", "_", corpus_id)

    return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"


def check_corpus_exists(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Comprueba si existe un corpus con el nombre dado.

    Args:
        corpus_name (str): El nombre del corpus a comprobar
        tool_context (ToolContext): El contexto de la herramienta para la gestión del estado
    
    Returns:
        bool: True si el corpus existe, False en caso contrario
    """

    if tool_context.state.get(f"corpus_exists_{corpus_name}"):
        return True

    try:
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        corpora = rag.list_corpora()
        for corpus in corpora:
            if (
                corpus.name == corpus_resource_name
                or corpus.display_name == corpus_name
            ):

                tool_context.state[f"corpus_exists_{corpus_name}"] = True

                if not tool_context.state.get("current_corpus"):
                    tool_context.state["current_corpus"] = corpus_name
                return True

        return False
    except Exception as e:
        logger.error(f"Error al comprobar si existe el corpus: {str(e)}")
        return False

def set_current_corpus(corpus_name: str, tool_context: ToolContext) -> bool:
    """
    Agregar el corpus actual en el estado del contexto de la herramienta.

    Args:
        corpus_name (str): El nombre del corpus para establecer como actual
        tool_context (ToolContext): El contexto de la herramienta para la gestión del estado

    Returns:
        bool: True si el corpus existe y se estableció como actual, False en caso contrario
    """
    
    if check_corpus_exists(corpus_name, tool_context):
        tool_context.state["current_corpus"] = corpus_name
        return True
    return False