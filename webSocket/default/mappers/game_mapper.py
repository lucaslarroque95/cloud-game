# mappers/game_mapper.py
from models.game import GameModel

class GameMapper:
    @staticmethod
    def to_dynamo(game: GameModel) -> dict:
        data = game.to_primitives()

        return {
            "roomId": data["room_id"],
            "board": data["board"],
            "turn": data["turn"],
            "status": data["status"],
            "createdAt": data["created_at"],
            "ttl": data["ttl"],
        }

    @staticmethod
    def from_dynamo(item: dict) -> GameModel:
        return GameModel(
            room_id=item["roomId"],
            board=item["board"],
            turn=item["turn"],
            status=item["status"],
            created_at=item["createdAt"],
            ttl=item["ttl"],
        )
