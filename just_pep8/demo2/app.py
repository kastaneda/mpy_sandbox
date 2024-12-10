import asyncio
import demo

def init():
    global led
    led = demo.MyDemoLED()

async def tick():
    while True:
        print('.', end='')
        await asyncio.sleep(1)

async def bomb():
    await asyncio.sleep(3)
    led.set_blink(True)
    await asyncio.sleep(5)
    led.set_value(1)
    await asyncio.sleep(3)
    1/0

async def main():
    asyncio.create_task(led.main())
    asyncio.create_task(bomb())
    await tick()

def deinit():
    pass
