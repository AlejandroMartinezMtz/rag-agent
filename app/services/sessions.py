import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def get_or_create_session(
    session_service,
    app_name: str,
    user_id: str,
    requested_session_id: Optional[str] = None
):
    session = None
    session_id = None

    if requested_session_id:
        try:
            session = await session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=requested_session_id
            )
            if session:
                session_id = session.id
                logger.info(f"Sesión recuperada por session_id: {session_id}")
                return session, session_id
        except Exception as e:
            logger.warning(f"No se pudo obtener sesión {requested_session_id}: {e}")

    try:
        list_resp = await session_service.list_sessions(app_name=app_name, user_id=user_id)
        sessions_list = getattr(list_resp, "sessions", []) or []

        if sessions_list:
            # tomar la de última actualización / creación
            def _ts(s):
                return (
                    getattr(s, "last_update_time", None)
                    or getattr(s, "create_time", None)
                    or 0
                )

            sessions_list.sort(key=_ts, reverse=True)
            session = sessions_list[0]
            session_id = session.id
            logger.info(f"Sesión más reciente encontrada: {session_id}")
            return session, session_id

    except Exception as e:
        logger.warning(f"Error listando sesiones para user {user_id}: {e}")

    try:
        initial_state = {}
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            state=initial_state
        )
        session_id = session.id
        logger.info(f"Nueva sesión creada: {session_id}")
        return session, session_id

    except Exception as create_error:
        raise RuntimeError(f"Error al crear sesión: {str(create_error)}")
