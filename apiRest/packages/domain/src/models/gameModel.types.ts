// models/game.types.ts

export type PlayerSymbol = "X" | "O";

export type GameStatus =
  | "CREATED"
  | "WAITING"
  | "PLAYING"
  | "FINISHED"
  | "EXPIRED";

export interface GameConfig {
  maxGameTimeSec: number;
  maxMoveTimeSec: number;
  startingPlayer: PlayerSymbol | "RANDOM";
}

export type Players = {
  X?: string;
  O?: string;
};

export interface GamePrimitives {
  gameId: string;
  status: GameStatus;
  config: GameConfig;
  players: Players;
  board: string[];
  turn: PlayerSymbol | null;
  winner?: PlayerSymbol | "DRAW";
  createdAt: number;   // unix epoch (mejor para Dynamo)
  updatedAt: number;
  ttl: number;
}

export const DEFAULT_GAME_CONFIG: GameConfig = {
maxGameTimeSec: 3600,
maxMoveTimeSec: 30,
startingPlayer: "X",
};