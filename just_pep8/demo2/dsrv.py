import asyncio

class MyDelayServo:
    def __init__(self):
        self.ev_update = asyncio.Event()
        self.delay = 1.5
        self.angle = 90

    def go(self, new_angle):
        if self.angle != new_angle:
            self.angle = new_angle
            self.ev_update.set()

    async def main(self):
        while True:
            await self.ev_update.wait() # to start updating
            try:
                self.ev_update.clear()
                print('+', self.angle, end='') # sg90.init(freq=50, duty_u16=u16)
                await asyncio.wait_for(self.ev_update.wait(), self.delay)
            except asyncio.TimeoutError:
                pass # normal, uninterrupted operation
            finally:
                print('-', end='') # sg90.deinit()
