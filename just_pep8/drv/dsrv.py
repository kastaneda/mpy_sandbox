import asyncio
import machine

class MyDelayServo:
    def __init__(self, gpio):
        self.servo = machine.PWM(machine.Pin(gpio, mode=machine.Pin.OUT))
        self.duty_u16 = None
        self.ev_update = asyncio.Event()

    def go(self, new_u16):
        new_u16 = int(new_u16)
        if self.duty_u16 != new_u16:
            self.duty_u16 = new_u16
            self.ev_update.set()

    async def main(self):
        while True:
            await self.ev_update.wait()
            try:
                self.ev_update.clear()
                self.servo.init(freq=50, duty_u16=self.duty_u16)
                await asyncio.wait_for_ms(self.ev_update.wait(), 500)
            except asyncio.TimeoutError:
                pass # uninterrupted move
            finally:
                self.servo.deinit()
