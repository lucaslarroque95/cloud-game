export type CreateGameRequest = {
    maxGameTimeSec?: number;
    maxMoveTimeSec?: number;
    startingPlayer?: "X" | "O" | "RANDOM";
};