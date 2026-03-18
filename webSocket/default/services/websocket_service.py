# services/websocket_service.py

class WebSocketService:
    def __init__(self, api_client):
        self.api_client = api_client

    def send(self, connection_id: str, message: str):
        self.api_client.post_to_connection(
            ConnectionId=connection_id,
            Data=message.encode("utf-8")
        )

    def disconnect(self, connection_id: str):
        self.api_client.delete_connection(ConnectionId=connection_id)