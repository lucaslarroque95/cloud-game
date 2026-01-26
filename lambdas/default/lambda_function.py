import json
import boto3

from helpers.response import _response
from helpers.ws_api_client import _create_ws_api_client

from repositories.player_repo import PlayerRepository
from repositories.game_repo import GameRepository

from services.websocket_service import WebSocketService
from services.game_service import GameService
from services.base_service import ServiceError

from handlers.init_handler import handle_init
from handlers.join_handler import handle_join
from handlers.play_handler import handle_play

# -------------------------
# Global
# -------------------------
ACTION_HANDLERS = {
    "INIT": handle_init,
    "JOIN": handle_join,
    "PLAY": handle_play,
}

dynamodb = boto3.resource("dynamodb")
player_table = dynamodb.Table("Players")
game_table = dynamodb.Table("Games")

# -------------------------
# Lambda handler
# -------------------------
def lambda_handler(event, context):
    request_context = event.get("requestContext", {})

    domain = request_context.get("domainName")
    stage = request_context.get("stage")
    connection_id = request_context.get("connectionId")

    if not domain or not stage:
        return _response(500, "Invalid WebSocket context")

    # Infra
    ws_client = _create_ws_api_client(domain, stage)
    ws_service = WebSocketService(ws_client)

    player_repo = PlayerRepository(player_table)
    game_repo = GameRepository(game_table)

    game_service = GameService(
        player_repo=player_repo,
        game_repo=game_repo,
        ws_service=ws_service
    )

    # -------------------------
    # Parse body
    # -------------------------
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return _response(400, "Invalid JSON payload")

    action = body.get("action")
    data = body.get("data", {})

    if not action:
        return _response(400, "Action not found in payload")

    print(f"📥 Action: {action} | Data: {data}")

    # -------------------------
    # Routing
    # -------------------------
    handler = ACTION_HANDLERS.get(action)
    if not handler:
        return _response(400, f"Unknown action: {action}")

    try:
        if action == "INIT":
            handler(game_service, connection_id)

        elif action == "JOIN":
            handler(game_service, connection_id, data)

        else:
            handler(game_service, data)

    except ServiceError as e:
        print(f"❌ Service error: {e}")
        return _response(500, str(e))

    except Exception as e:
        print(f"🔥 Unexpected error: {e}")
        return _response(500, "Internal server error")

    return _response(200, "OK")