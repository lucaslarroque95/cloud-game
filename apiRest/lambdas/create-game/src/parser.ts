import { CreateGameRequest } from "./types";

export function parseCreateGameRequest(
  body: string | null
): CreateGameRequest {
  if (!body) return {};

  let parsed: unknown;

  try {
    parsed = JSON.parse(body);
  } catch {
    throw new Error("Invalid JSON body");
  }

  if (typeof parsed !== "object" || parsed === null) {
    throw new Error("Body must be an object");
  }

  return parsed as CreateGameRequest;
}
