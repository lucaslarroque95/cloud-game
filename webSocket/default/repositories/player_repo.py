# repositories/player_repo.py
import time

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from mappers.player_mapper import PlayerMapper


class PlayerRepository:
    def __init__(self, table):
        self.table = table
    
    def get_opponent(self, player_id: str):
        last_evaluated_key = None
        while last_evaluated_key is not False:
            query_kwargs = {
                "IndexName": "GSI_Status",
                "KeyConditionExpression": Key("status").eq("WAITING"),
                "FilterExpression": Attr("playerId").ne(player_id),
                "ScanIndexForward": True,
                "Limit": 2
            }
            if last_evaluated_key:
                query_kwargs["ExclusiveStartKey"] = last_evaluated_key

            resp = self.table.query(**query_kwargs)
            items = resp.get("Items", [])
            if items:
                return PlayerMapper.from_dynamo(items[0])

            last_evaluated_key = resp.get("LastEvaluatedKey", False)

        return None



    def get_room_players(self, room_id: str):
        query_kwargs = {"IndexName": "GSI_Room", "KeyConditionExpression": Key("roomId").eq(room_id)}
        resp = self.table.query(**query_kwargs)
        items = resp.get("Items", [])
        if items:
            new_items = []
            for item in items:
                new_item = PlayerMapper.from_dynamo(item)
                new_items.append(new_item)
            
            return new_items

        return None

    def create(self, item):
        item = PlayerMapper.to_dynamo(item)
        self.table.put_item(Item=item, ConditionExpression="attribute_not_exists(playerId)")


    def update(self, item):
        item = PlayerMapper.to_dynamo(item)

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

        if item.get("roomId") is not None:
            update_expr_parts.append("#r = :room")
            expr_attr_names["#r"] = "roomId"
            expr_attr_values[":room"] = item["roomId"]

        if item.get("symbol") is not None:
            update_expr_parts.append("#o = :symbol")
            expr_attr_names["#o"] = "symbol"
            expr_attr_values[":symbol"] = item["symbol"]

        # 🔒 No actualizar si no hay nada
        if not update_expr_parts:
            return

        update_expression = "SET " + ", ".join(update_expr_parts)

        self.table.update_item(
            Key={"playerId": item.get("playerId")},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expr_attr_names if expr_attr_names else None,
            ExpressionAttributeValues=expr_attr_values
        )
    
    def delete(self, player_id):
        now = int(time.time())
        self.table.update_item(
            Key={"playerId": player_id},
            UpdateExpression="""SET #s = :d, ttl = :ttl""",
            ConditionExpression="#s <> :d",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":d": "DISCONNECTED", ":ttl": now + 10}
        )

