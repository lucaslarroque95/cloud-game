import { GameModel, GameRepository, awsCall } from "@game/domain";
import { parseCreateGameRequest } from "./parser";

export const handler = async (event: any) => {
  const input = parseCreateGameRequest(event.body);

  const game = GameModel.create({
    startingPlayer: input.startingPlayer ?? "RANDOM",
    maxGameTimeSec: input.maxGameTimeSec ?? 3600,
    maxMoveTimeSec: input.maxMoveTimeSec ?? 30,
  });

  const repo = new GameRepository("Games");

  await awsCall(
    () => repo.create(game),
    "Error creating game"
  );

  return {
    statusCode: 201,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify({ gameId: game.gameId }),
  };
};
