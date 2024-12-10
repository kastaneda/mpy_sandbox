import asyncio

class MyDemoLED:
    def __init__(self):
        self.event_update = asyncio.Event()
        self.blink_endless = False
        self.delay_on = .5
        self.delay_off = .5

    def value(self, new_state):
        print(int(new_state), end='')

    def set_value(self, new_state):
        self.blink_endless = False
        self.value(new_state)
        self.event_update.set()

    def set_blink(self, new_state):
        self.blink_endless = new_state
        self.event_update.set()

    def toggle_blink(self):
        self.blink_endless = not self.blink_endless
        self.event_update.set()

    async def main(self):
        while True:
            if self.blink_endless:
                while not self.event_update.is_set():
                    self.value(1)
                    await asyncio.sleep(self.delay_on)
                    self.value(0)
                    await asyncio.sleep(self.delay_off)
                self.event_update.clear()
            else:
                await self.event_update.wait()
                self.event_update.clear()
