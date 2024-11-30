#!/usr/bin/python3

import asyncio

class DummyLed():
    _val = 0

    def value(self, val=None):
        if val == None:
            return self._val
        self._val = val
        print('LED state:', self._val)

    def toggle(self):
        self.value(1 - self.value())

class MyLedBlinker():

    def __init__(self, led):
        self._led = led
        self._times_to_flash = 0
        self._event = asyncio.Event()

    def set(self, val):
        self._led.value(val)

    async def blink_coro(self):
        while True:
            await self._event.wait()
            self._event.clear()
            while self._times_to_flash > 0:
                self._times_to_flash -= 1
                self._led.toggle()
                await asyncio.sleep(0.1)

    def start_blinking(self, times):
        self._times_to_flash += 2*times
        self._event.set()

async def debug_tick():
    while True:
        print('Tick')
        await asyncio.sleep(1)

gpio2_blinker = MyLedBlinker(DummyLed())

async def main(blinker):
    print('Prepare')
    asyncio.create_task(debug_tick())
    asyncio.create_task(blinker.blink_coro())
    await asyncio.sleep(2.5)
    blinker.start_blinking(3)
    await asyncio.sleep(0.5)
    blinker.start_blinking(2)
    await asyncio.sleep(1.5)
    print('Done')

asyncio.run(main(gpio2_blinker))

