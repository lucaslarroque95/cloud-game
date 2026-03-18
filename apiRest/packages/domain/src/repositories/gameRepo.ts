// repositories/gameRepo.ts

  import {
    DynamoDBDocumentClient,
    GetCommand,
    PutCommand,
    UpdateCommand,
  } from "@aws-sdk/lib-dynamodb";
  import { DynamoDBClient } from "@aws-sdk/client-dynamodb";

  
  import { GameMapper } from "../mappers/gameMapper";
  
  export class GameRepository {
    private readonly db: DynamoDBDocumentClient;
  
    constructor(private readonly tableName: string) {
      this.db = DynamoDBDocumentClient.from(
        new DynamoDBClient({})
      );
    }
  
    async get(roomId: string) {
      const resp = await this.db.send(
        new GetCommand({
          TableName: this.tableName,
          Key: { roomId },
        })
      );
  
      if (!resp.Item) return null;
  
      return GameMapper.fromDynamo(resp.Item);
    }
  
    async create(item: any) {
      const dynamoItem = GameMapper.toDynamo(item);
  
      console.log(dynamoItem);
  
      await this.db.send(
        new PutCommand({
          TableName: this.tableName,
          Item: dynamoItem,
          ConditionExpression: "attribute_not_exists(roomId)",
        })
      );
    }
  
    async update(item: any) {
      const dynamoItem = GameMapper.toDynamo(item);
  
      const updateParts: string[] = [];
      const exprAttrValues: Record<string, any> = {};
      const exprAttrNames: Record<string, string> = {};
  
      if (dynamoItem.status !== undefined) {
        updateParts.push("#s = :status");
        exprAttrNames["#s"] = "status";
        exprAttrValues[":status"] = dynamoItem.status;
      }
  
      if (dynamoItem.createdAt !== undefined) {
        updateParts.push("#c = :created");
        exprAttrNames["#c"] = "createdAt";
        exprAttrValues[":created"] = dynamoItem.createdAt;
      }
  
      if (dynamoItem.ttl !== undefined) {
        updateParts.push("#ttl = :ttl");
        exprAttrNames["#ttl"] = "ttl";
        exprAttrValues[":ttl"] = dynamoItem.ttl;
      }
  
      if (dynamoItem.board !== undefined) {
        updateParts.push("#b = :board");
        exprAttrNames["#b"] = "board";
        exprAttrValues[":board"] = dynamoItem.board;
      }
  
      if (dynamoItem.turn !== undefined) {
        updateParts.push("#t = :turn");
        exprAttrNames["#t"] = "turn";
        exprAttrValues[":turn"] = dynamoItem.turn;
      }
  
      // 🔒 no actualizar si no hay nada
      if (updateParts.length === 0) return;
  
      const updateExpression = `SET ${updateParts.join(", ")}`;
  
      await this.db.send(
        new UpdateCommand({
          TableName: this.tableName,
          Key: { roomId: dynamoItem.roomId },
          UpdateExpression: updateExpression,
          ExpressionAttributeNames: exprAttrNames,
          ExpressionAttributeValues: exprAttrValues,
        })
      );
    }
  
    async delete(roomId: string) {
      const now = Math.floor(Date.now() / 1000);
  
      await this.db.send(
        new UpdateCommand({
          TableName: this.tableName,
          Key: { roomId },
          UpdateExpression: "SET #s = :d, ttl = :ttl",
          ConditionExpression: "#s <> :d",
          ExpressionAttributeNames: {
            "#s": "status",
          },
          ExpressionAttributeValues: {
            ":d": "GAME OVER",
            ":ttl": now + 10,
          },
        })
      );
    }
  }
  