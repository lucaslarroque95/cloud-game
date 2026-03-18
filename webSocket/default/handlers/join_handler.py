# handlers/join_handler.py

from services.base_service import ServiceError

def handle_join(game_service, connection_id: str, data: dict):
    player_id = data.get("playerId")

    if not connection_id:
        raise ServiceError("ConnectionId not found")
    if not player_id:
        raise ServiceError("PlayerId not found")

    game_service.join(player_id, connection_id)