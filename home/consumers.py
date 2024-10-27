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
            bufsize=1,  # Line-buffered
            universal_newlines=True #Text mode
        )
        
        # for line in iter(process.stdout.readline, ''):
        #     output_line = line.strip()
        #     # output_line = line.decode('utf-8')
        #     await self.send(text_data=json.dumps({'output': output_line.strip()}))
        #     print("Script output:", output_line)  # Log output for debugging
        
        # for output_line in iter(process.stdout.readline, ''):
        #     if output_line.strip():
        #         await self.send(text_data=json.dumps({'output': output_line.strip()}))
        #         print("Script output:", output_line.strip())
            
        for line in iter(process.stdout.readline, ''):
            output_line = line.strip()
            if output_line:
                await self.send(text_data=json.dumps({'output': output_line}))
                print("Script output:", output_line)  # Log output for debugging
            else:
                break