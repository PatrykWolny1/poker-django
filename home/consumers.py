# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# import subprocess

# class ScriptConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         print("WebSocket connected.")

#     async def disconnect(self, close_code):
#         print("WebSocket disconnected.")

#     async def receive(self, text_data):
#         print("Received data:", text_data)  # Log input received
#         data = json.loads(text_data)
#         user_input = data['input']

#         process = subprocess.Popen(
#             ['python', 'hello.py', user_input],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )

#         for line in iter(process.stdout.readline, b''):
#             output_line = line.decode('utf-8')
#             await self.send(text_data=json.dumps({'output': output_line}))
#             print("Script output:", output_line)  # Log output for debugging
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_data_task()

    async def disconnect(self, close_code):
        pass

    # async def get_data(self):
    #     # Replace with your real-time data logic
    #     while True
    #     return {"message": "Hello, world!"}
    
    async def send_data_task(self):
        for number in range(1, 11):  # Send numbers from 1 to 10
            data = {'message': number}
            await self.send(text_data=json.dumps(data))
            await asyncio.sleep(1) 
        