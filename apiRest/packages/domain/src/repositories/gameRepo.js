"use strict";
// repositories/gameRepo.ts
Object.defineProperty(exports, "__esModule", { value: true });
exports.GameRepository = void 0;
const lib_dynamodb_1 = require("@aws-sdk/lib-dynamodb");
const client_dynamodb_1 = require("@aws-sdk/client-dynamodb");
const gameMapper_1 = require("../mappers/gameMapper");
class GameRepository {
    constructor(tableName) {
        this.tableName = tableName;
        this.db = lib_dynamodb_1.DynamoDBDocumentClient.from(new client_dynamodb_1.DynamoDBClient({}));
    }
    async get(roomId) {
        const resp = await this.db.send(new lib_dynamodb_1.GetCommand({
            TableName: this.tableName,
            Key: { roomId },
        }));
        if (!resp.Item)
            return null;
        return gameMapper_1.GameMapper.fromDynamo(resp.Item);
    }
    async create(item) {
        const dynamoItem = gameMapper_1.GameMapper.toDynamo(item);
        console.log(dynamoItem);
        await this.db.send(new lib_dynamodb_1.PutCommand({
            TableName: this.tableName,
            Item: dynamoItem,
            ConditionExpression: "attribute_not_exists(roomId)",
        }));
    }
    async update(item) {
        const dynamoItem = gameMapper_1.GameMapper.toDynamo(item);
        const updateParts = [];
        const exprAttrValues = {};
        const exprAttrNames = {};
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
        if (updateParts.length === 0)
            return;
        const updateExpression = `SET ${updateParts.join(", ")}`;
        await this.db.send(new lib_dynamodb_1.UpdateCommand({
            TableName: this.tableName,
            Key: { roomId: dynamoItem.roomId },
            UpdateExpression: updateExpression,
            ExpressionAttributeNames: exprAttrNames,
            ExpressionAttributeValues: exprAttrValues,
        }));
    }
    async delete(roomId) {
        const now = Math.floor(Date.now() / 1000);
        await this.db.send(new lib_dynamodb_1.UpdateCommand({
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
        }));
    }
}
exports.GameRepository = GameRepository;
