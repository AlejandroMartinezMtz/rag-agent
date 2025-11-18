import os
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")


def create_session_service():
    return VertexAiSessionService(
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION
    )


def create_memory_bank_service():
    return VertexAiMemoryBankService(
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION
    )
