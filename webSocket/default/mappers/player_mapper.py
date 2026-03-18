# mappers/player_mapper.py
from models.player import PlayerModel

class PlayerMapper:

    @staticmethod
    def to_dynamo(player: PlayerModel) -> dict:
        player_dict = player.to_primitives()

        data = {
            "playerId": player_dict["player_id"],
            "connectionId": player_dict["connection_id"],
            "status": player_dict["status"],
            "ttl": player_dict["ttl"],
            "createdAt": player_dict["created_at"],
        }

        if player_dict.get("room_id") is not None:
            data["roomId"] = player_dict["room_id"]

        if player_dict.get("symbol") is not None:
            data["symbol"] = player_dict["symbol"]

        return data

    @staticmethod
    def from_dynamo(item: dict) -> PlayerModel:
        return PlayerModel(
            player_id=item["playerId"],
            connection_id=item["connectionId"],
            status=item["status"],
            ttl=item["ttl"],
            room_id=item.get("roomId"),
            symbol=item.get("symbol"),
            created_at=item.get("createdAt"),
        )
