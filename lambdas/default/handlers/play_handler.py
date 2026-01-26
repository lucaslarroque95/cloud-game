# handlers/play_handler.py

from services.base_service import ServiceError

def handle_play(game_service, data: dict):
    player_id = data.get("playerId")
    room_id = data.get("roomId")
    board = data.get("board")

    if not player_id:
        raise ServiceError("PlayerId not found")
    if not room_id:
        raise ServiceError("RoomId not found")
    if not board:
        raise ServiceError("Board not found")

    game_service.play(room_id, board, player_id)