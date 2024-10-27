import json
from channels.generic.websocket import AsyncWebsocketConsumer
import subprocess

class ScriptConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connected.")

    async def disconnect(self, close_code):
        print("WebSocket disconnected.")

    async def receive(self, text_data):
        print("Received data:", text_data)  # Log input received
        data = json.loads(text_data)
        user_input = data['input']

        process = subprocess.Popen(
            ['python', 'hello.py', user_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        for line in iter(process.stdout.readline, b''):
            output_line = line.decode('utf-8')
            await self.send(text_data=json.dumps({'output': output_line}))
            print("Script output:", output_line)  # Log output for debugging