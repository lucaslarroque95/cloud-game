
import { GameModel } from "../models/gameModel";

export class GameMapper {
  static toDynamo(game: GameModel): Record<string, any> {
    const data = game.toPrimitives();

    return {
      gameId: data.gameId,
      status: data.status,
      config: data.config,
      players: data.players,
      board: data.board,
      turn: data.turn,
      winner: data.winner,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
      ttl: data.ttl,
    };
  }

  static fromDynamo(item: Record<string, any>): GameModel {
    return GameModel.fromPrimitives({
        gameId: item.gameId,
        status: item.status,
        config: item.config,
        players: item.players,
        board: item.board,
        turn: item.turn,
        winner: item.winner,
        createdAt: item.createdAt,
        updatedAt: item.updatedAt,
        ttl: item.ttl
    });
  }
}