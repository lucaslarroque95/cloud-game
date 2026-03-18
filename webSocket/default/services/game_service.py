# services/game_service.py
import json
import time

from services.base_service import aws_call
from models.player import PlayerModel
from models.game import GameModel
from rules.evaluate import evaluate_match


class GameService:
    def __init__(self, player_repo, game_repo, ws_service):
        self.player_repo = player_repo
        self.game_repo = game_repo
        self.ws = ws_service

    # -------------------------
    # Helpers internos
    # -------------------------
    def _notify(self, connection_id: str, payload: dict):
        aws_call(
            lambda: self.ws.send(connection_id, json.dumps(payload)),
            "Error sending websocket message"
        )

    def _disconnect(self, connection_id: str):
        aws_call(
            lambda: self.ws.disconnect(connection_id),
            "Error disconnecting websocket"
        )
    
    def _split_players(self, players: list[dict], player_id: str):
        if len(players) != 2:
            raise ValueError("Invalid room state: room must have exactly 2 players")

        player = next((p for p in players if p.player_id == player_id), None)
        if not player:
            raise ValueError(f"Player {player_id} not found in room")

        opponent = next((p for p in players if p.player_id != player_id), None)
        if not opponent:
            raise ValueError("Opponent not found in room")

        return player, opponent

    def _assign_players(self, game, player, opponent):
        """
        Assigns both players to a game room and updates their state.
        """
        # El jugador que llamó a join siempre es X
        player.join_game(
            room_id=game.room_id,
            symbol="X",
            ttl=3600
        )

        # Oponente siempre es O
        opponent.join_game(
            room_id=game.room_id,
            symbol="O",
            ttl=3600
        )

        return player, opponent

    def _handle_status(self, status, game, player, opponent):
        action = None
        # -------------------------
        # WIN
        # -------------------------
        if status == player.symbol:
            game.set_status("GAME_OVER")
            player.set_status("WIN")
            opponent.set_status("LOSE")

            notify = [player, opponent]
            update_players = True
            disconnect = True
            turn = False
        # -------------------------
        # DRAW
        # -------------------------
        elif status == "DRAW":
            game.set_status("DRAW")
            player.set_status("DRAW")
            opponent.set_status("DRAW")
            
            notify = [player, opponent]
            update_players = True
            disconnect = True
            turn = False
        
        # -------------------------
        # CONTINUE GAME
        # -------------------------
        else:
            action = "PLAY"
            notify = [opponent]
            update_players = False
            disconnect = False
            turn = True

        aws_call(
            lambda: self.game_repo.update(game),
            "Error updating game"
        )
        
        if update_players:
            aws_call(
                lambda: self.player_repo.update(player),
                "Error updating player status"
            )

            aws_call(
                lambda: self.player_repo.update(opponent),
                "Error updating opponent status"
            )

        for player in notify:
            self._notify(player.connection_id, {
                "type": action if action else player.status,
                "data": {
                    "playerId": player.player_id,
                    "roomId": game.room_id,
                    "board": game.board,
                    "symbol": player.symbol,
                    "turn": turn
                }
            })

            if disconnect:
                self._disconnect(player.connection_id)

    # -------------------------
    # Public API
    # -------------------------
    def init(self, connection_id: str):
        player = PlayerModel.waiting(connection_id, ttl=3600)

        aws_call(
            lambda: self.player_repo.create(player),
            "Error creating player"
        )

        self._notify(connection_id, {
            "type": "INIT",
            "data": {"playerId": player.player_id}
        })

    def join(self, player_id: str, connection_id: str):
        player = PlayerModel(
            player_id=player_id,
            connection_id=connection_id
        )

        opponent = aws_call(
            lambda: self.player_repo.get_opponent(player.player_id),
            "Error getting opponent"
        )

        if not opponent:
            self._notify(connection_id, {
                "type": "WAIT",
                "data": {"playerId": player.player_id}
            })
            return

        game = GameModel.new(ttl=3600)
        aws_call(lambda: self.game_repo.create(game), "Error creating game")

        notify = self._assign_players(game, player, opponent)
        
        for player in notify:
            aws_call(
                lambda: self.player_repo.update(player),
                "Error updating player"
            )

            self._notify(player.connection_id, {
                "type": "START",
                "data": {
                    "playerId": player.player_id,
                    "roomId": game.room_id,
                    "board": game.board,
                    "symbol": player.symbol,
                    "turn": player.symbol == game.turn
                }
            })

    def play(self, room_id: str, board: list, player_id: str):
        players = aws_call(
            lambda: self.player_repo.get_room_players(room_id),
            "Error getting room players"
        )

        player, opponent = self._split_players(players, player_id)

        game = aws_call(
            lambda: self.game_repo.get(room_id),
            "Error getting game"
        )
        if not game:
            raise ValueError("Error getting game")

        game.set_board(board)
        game.set_turn(opponent.symbol)

        status = evaluate_match(board)
        self._handle_status(status, game, player, opponent)