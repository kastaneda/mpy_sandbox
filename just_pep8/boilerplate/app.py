import asyncio
import time

def init():
    print('Connecting to Wi-Fi...', end='')
    time.sleep(1)
    print(' done')

    print('Connecting to MQTT broker...', end='')
    time.sleep(.5)
    print(' done')

async def tick():
    while True:
        print('.', end='')
        await asyncio.sleep(1)

async def bomb():
    await asyncio.sleep(5)
    1/0

async def main():
    asyncio.create_task(bomb())
    await tick()

def deinit():
    print('Disconnecting from MQTT broker')
