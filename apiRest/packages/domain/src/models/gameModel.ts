// models/game.model.ts

import { randomUUID } from "crypto";
import {GamePrimitives, PlayerSymbol, GameConfig, DEFAULT_GAME_CONFIG} from "./gameModel.types";

export class GameModel {
  private constructor(private readonly props: GamePrimitives) {}

  // 🏗️ Factory: crear nuevo juego
  static create(config: Partial<GameConfig> = {}): GameModel {
    const now = Math.floor(Date.now() / 1000);
    const ttl = 3600;

    const finalConfig: GameConfig = {
      ...DEFAULT_GAME_CONFIG,
      ...config,
    };
  
    return new GameModel({
      gameId: randomUUID(),
      status: "PLAYING",
      config: finalConfig,
      players: {},
      board: Array(9).fill(""),
      turn:
        finalConfig.startingPlayer === "RANDOM"
          ? Math.random() > 0.5
            ? "X"
            : "O"
          : finalConfig.startingPlayer,
      createdAt: now,
      updatedAt: now,
      ttl: now + ttl,
    });
  }

  // 🔄 Reconstruir desde Dynamo / repo
  static fromPrimitives(data: GamePrimitives): GameModel {
    return new GameModel(data);
  }

  // 📤 Para persistencia / transporte
  toPrimitives(): GamePrimitives {
    return { ...this.props };
  }

  // 🧠 Getters útiles
  get gameId() {
    return this.props.gameId;
  }

  get status() {
    return this.props.status;
  }

  get turn(): PlayerSymbol | null {
    return this.props.turn;
  }

  isFinished(): boolean {
    return this.props.status === "FINISHED";
  }
}
