import asyncio

class MyDelayServo:
    def __init__(self):
        self.event_update = asyncio.Event()
        self.delay = 1.5
        self.angle = 90

    def go(self, new_angle):
        if self.angle != new_angle:
            self.angle = new_angle
            self.event_update.set()

    async def main(self):
        while True:
            await self.event_update.wait() # to start updating
            try:
                self.event_update.clear()
                print('+', self.angle, end='') # sg90.init(freq=50, duty_u16=u16)
                await asyncio.wait_for(self.event_update.wait(), self.delay)
            except asyncio.TimeoutError:
                pass
            finally:
                print('-', end='') # sg90.deinit()
