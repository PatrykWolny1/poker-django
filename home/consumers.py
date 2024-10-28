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
            ['python', 'C:/Users/patry/VSCode/poker-django/main.py'],
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
            print(output.strip())