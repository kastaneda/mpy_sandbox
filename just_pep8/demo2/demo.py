import asyncio

class MyDemoLED:
    pub = lambda x: None
#   blink_endless = False

    def __init__(self):
        self.value(0)
#       self.event = new asyncio.Event()

    def value(self, new_state):
        print(int(new_state), end='')

    def set_value(self, new_state):
#       self.blink_endless = False
        self.value(new_state)

#   def set_blink(self, new_state):
#       self.blink_endless = new_state

    async def main(self):
        while True:
            self.value(1)
            await asyncio.sleep(.5)
            self.value(0)
            await asyncio.sleep(.5)
