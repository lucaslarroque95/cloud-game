# model/game.py
import time
import uuid

class GameModel:
    def __init__(
        self,
        room_id: str,
        board: list[str] | None = None,
        turn: str | None = None,
        status: str | None = None,
        created_at: int | None = None,
        ttl: int | None = None
    ):
        self.room_id = room_id
        self.board = board
        self.turn = turn
        self.status = status
        self.created_at = created_at
        self.ttl = ttl

    def set_status(self, status):
        self.status = status
    
    def set_board(self, board):
        self.board = board
    
    def set_turn(self, turn):
        self.turn = turn

    @classmethod
    def new(cls, ttl: int):
        now = int(time.time())
        return cls(
            room_id=str(uuid.uuid4()),
            board=[""] * 9,
            turn="X",
            status="PLAYING",
            created_at=now,
            ttl=now + ttl,
        )

    def to_primitives(self) -> dict:
        return {
            "room_id": self.room_id,
            "board": self.board,
            "turn": self.turn,
            "status": self.status,
            "created_at": self.created_at,
            "ttl": self.ttl,
        }