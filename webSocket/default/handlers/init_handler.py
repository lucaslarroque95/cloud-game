# handlers/init_handler.py

from services.base_service import ServiceError

def handle_init(game_service, connection_id: str):
    if not connection_id:
        raise ServiceError("ConnectionId not found")

    game_service.init(connection_id)
