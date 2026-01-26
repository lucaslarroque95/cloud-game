# models/player.py
import uuid
import time

class PlayerModel:
    def __init__(
        self,
        player_id: str,
        connection_id: str,
        status: str | None = None,
        created_at: int | None = None,
        ttl: int | None = None,
        room_id: str | None = None,
        symbol: str | None = None,
    ):
        self.player_id = player_id
        self.connection_id = connection_id
        self.status = status
        self.created_at = created_at
        self.ttl = ttl
        self.room_id = room_id
        self.symbol = symbol

    # -------------------------
    # Factories de dominio
    # -------------------------
    @classmethod
    def waiting(cls, connection_id: str, ttl: int):
        now = int(time.time())
        return cls(
            player_id=str(uuid.uuid4()),
            connection_id=connection_id,
            status="WAITING",
            created_at=now,
            ttl=now+ttl,
        )
    
    def join_game(self, room_id: str, symbol: str, ttl: int):
        now = int(time.time())
        self.room_id = room_id
        self.symbol = symbol
        self.status = "PLAYING"
        self.ttl = now + ttl

    def set_status(self, status):
        self.status = status
    
    
    @classmethod
    def from_primitives(
        cls,
        *,
        player_id: str,
        connection_id: str,
        status: str,
        ttl: int,
        room_id: str | None = None,
        symbol: str | None = None,
        created_at: int | None = None,
    ):
        return cls(
            player_id=player_id,
            connection_id=connection_id,
            status=status,
            ttl=ttl,
            room_id=room_id,
            symbol=symbol,
            created_at=created_at,
        )

    def to_primitives(self) -> dict:
        return {
            "player_id": self.player_id,
            "connection_id": self.connection_id,
            "status": self.status,
            "ttl": self.ttl,
            "room_id": self.room_id,
            "symbol": self.symbol,
            "created_at": self.created_at,
        }