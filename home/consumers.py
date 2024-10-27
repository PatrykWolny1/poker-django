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
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# import asyncio

# class MyConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send_data_task()

#     async def disconnect(self, close_code):
#         pass

#     # async def get_data(self):
#     #     # Replace with your real-time data logic
#     #     while True
#     #     return {"message": "Hello, world!"}
    
#     async def send_data_task(self):
#         for number in range(1, 11):  # Send numbers from 1 to 10
#             data = {'message': number}
#             await self.send(text_data=json.dumps(data))
#             await asyncio.sleep(1) 


import json
import asyncio
import subprocess
from channels.generic.websocket import AsyncWebsocketConsumer

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_data_task()

    async def disconnect(self, close_code):
        pass

    async def send_data_task(self):
        # Replace 'your_script.py' with the path to your script
        process = subprocess.Popen(
            ['python', '../main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        while True:
            output = await asyncio.get_event_loop().run_in_executor(None, process.stdout.readline)
            if output:
                # Send the output to WebSocket clients
                await self.send(text_data=json.dumps({'message': output.strip()}))
            elif process.poll() is not None:
                break  # Exit if the process has finished
            await asyncio.sleep(0.1)  # Avoid busy waiting