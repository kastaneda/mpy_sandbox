import asyncio
import machine

class MyDemoLED:
    pub = lambda x: None
#   blink_endless = False

    def __init__(self, gpio, callback=None, val_on=1, val_off=0):
        self.led = machine.Pin(gpio, machine.Pin.OUT)
        self.value_on = val_on
        self.value_off = val_off
        if callback:
            self.pub = callback
        self.value(0)
#       self.event = new asyncio.Event()

    def value(self, new_state):
        new_value = self.value_on if new_state else self.value_off
        if self.led.value() != new_value:
            self.led.value(new_value)
            self.pub(new_state)

    def set_value(self, new_state):
#       self.blink_endless = False
        self.value(new_state)

#   def set_blink(self, new_state):
#       self.blink_endless = new_state

    async def main(self):
        while True:
            self.value(1)
            await asyncio.sleep_ms(500)
            self.value(0)
            await asyncio.sleep_ms(500)
