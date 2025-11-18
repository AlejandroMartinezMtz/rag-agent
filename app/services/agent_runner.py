"""
Construye el Runner y controla la creación/obtención de sesiones.
"""

import uuid
from google.adk import Runner

from services.session_service import SessionService
from services.vertex_services import VertexServices
from agent.agent import root_agent


class AgentRunner:
    """
    Clase que encapsula la creación del Runner de ADK
    y administra la sesión del usuario.
    """

    def __init__(self, project_id: str, location: str):
        self.project_id = project_id
        self.location = location

        self.session_service = SessionService()
        self.vertex = VertexServices(project_id, location)
        self.agent = root_agent

    def get_or_create_session(self, session_id: str | None = None) -> str:
        """
        Regresa una sesión válida. Si no existe, la crea.
        """
        if session_id:
            exists = self.session_service.exists(session_id)
            if exists:
                return session_id

        new_session_id = str(uuid.uuid4())
        self.session_service.create(new_session_id)
        return new_session_id

    def build(self, session_id: str) -> Runner:
        session = self.session_service.get(session_id)
        agent = self.agent_factory.create_agent(session_id=session_id)

        runner = Runner(
            agent=agent,
            session=session,
            memory_bank=self.vertex.build_memory_bank(),
        )

        return runner
