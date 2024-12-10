import asyncio
import machine

class MyDemoLED:
    pub = lambda x: None
    blink_endless = False
    delay_on = 500
    delay_off = 500

    def __init__(self, gpio, callback=None, val_on=1, val_off=0):
        self.led = machine.Pin(gpio, machine.Pin.OUT)
        self.value_on = val_on
        self.value_off = val_off
        if callback:
            self.pub = callback
        self.value(0)
        self.ev_update = asyncio.Event()

    def value(self, new_state):
        new_value = self.value_on if new_state else self.value_off
        if self.led.value() != new_value:
            self.led.value(new_value)
            self.pub(new_state)

    def set_value(self, new_state):
        new_state = int(new_state)
        self.blink_endless = False
        self.value(new_state)
        self.ev_update.set()

    def set_blink(self, new_state):
        new_state = bool(int(new_state))
        self.blink_endless = new_state
        self.ev_update.set()

    def toggle_blink(self):
        self.set_blink(not self.blink_endless)

    async def main(self):
        while True:
            if self.blink_endless:
                while not self.ev_update.is_set():
                    self.value(1)
                    await asyncio.sleep_ms(self.delay_on)
                    self.value(0)
                    await asyncio.sleep_ms(self.delay_off)
                self.ev_update.clear()
            else:
                await self.ev_update.wait()
                self.ev_update.clear()