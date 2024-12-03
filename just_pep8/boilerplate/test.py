import asyncio
import time

class MyTestApp:
    def __init__(self):
        print('Connecting to Wi-Fi...', end='')
        time.sleep(1)
        print(' done')
        print('Connecting to MQTT broker...', end='')
        time.sleep(0.5)
        print(' done')

    async def tick(self):
        while True:
            print('.', end='')
            await asyncio.sleep(1)

    async def bomb(self):
        await asyncio.sleep(5)
        1/0

    def main(self):
        asyncio.create_task(self.tick())
        asyncio.create_task(self.bomb())

    def deinit(self):
        print('Disconnecting from MQTT broker')
