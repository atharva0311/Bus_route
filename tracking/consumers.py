from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LiveBusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # All users join the same group to receive live bus updates
        self.group_name = "live_buses"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive messages from WebSocket (optional if driver uses WebSocket)
    async def receive(self, text_data):
        pass  # we push updates from server-side, driver posts via API

    # Send location updates to clients
    async def send_location(self, event):
        await self.send(text_data=json.dumps(event))
