# repositories/game_repo.py

import time

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from mappers.game_mapper import GameMapper

class GameRepository:
    def __init__(self, table):
        self.table = table
    
    def get(self, room_id):
        resp = self.table.get_item(Key={"roomId": room_id})
        item = resp.get("Item")
        if item:
            item = GameMapper.from_dynamo(item)
            return item
        
        return None

    def create(self, item):
        item = GameMapper.to_dynamo(item)
        print(item)
        self.table.put_item(Item=item,ConditionExpression="attribute_not_exists(roomId)")
    
    def update(self, item):
        item = GameMapper.to_dynamo(item)

        update_expr_parts = []
        expr_attr_values = {}
        expr_attr_names = {}
        
        if item.get("status") is not None:
            update_expr_parts.append("#s = :status")
            expr_attr_names["#s"] = "status"
            expr_attr_values[":status"] = item["status"]
        
        if item.get("createdAt") is not None:
            update_expr_parts.append("#c = :created")
            expr_attr_names["#c"] = "createdAt"
            expr_attr_values[":created"] = item["createdAt"]

        if item.get("ttl") is not None:
            update_expr_parts.append("#ttl = :ttl")
            expr_attr_names["#ttl"] = "ttl"
            expr_attr_values[":ttl"] = item["ttl"]

        if item.get("board") is not None:
            update_expr_parts.append("#b = :board")
            expr_attr_names["#b"] = "board"
            expr_attr_values[":board"] = item["board"]

        if item.get("turn") is not None:
            update_expr_parts.append("#t = :turn")
            expr_attr_names["#t"] = "turn"
            expr_attr_values[":turn"] = item["turn"]

        # 🔒 No actualizar si no hay nada
        if not update_expr_parts:
            return

        update_expression = "SET " + ", ".join(update_expr_parts)

        self.table.update_item(
            Key={"roomId": item.get("roomId")},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expr_attr_names if expr_attr_names else None,
            ExpressionAttributeValues=expr_attr_values
        )
    
    def delete(self, room_id):
        now = int(time.time())
        self.table.update_item(
            Key={"playerId": room_id},
            UpdateExpression="SET #s = :d, ttl = :ttl",
            ConditionExpression="#s <> :d",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":d": "GAME OVER", ":ttl": now + 10}
        )

        

