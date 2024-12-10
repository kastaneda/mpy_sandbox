import asyncio
import machine

class MyDingDong:
    def __init__(self, gpio, callback):
        self.ev_click = asyncio.Event()
        self.onclick = callback
        self.btn = machine.Pin(gpio, machine.Pin.IN, machine.Pin.PULL_UP)
        self.btn.irq(
            trigger=machine.Pin.IRQ_FALLING,
            handler=self.handle_click)

    def handle_click(self, pin):
        self.ev_click.set()

    async def main(self):
        while True:
            await self.ev_click.wait()
            self.ev_click.clear()
            print('B', end='')
            await asyncio.sleep_ms(250) # Very silly debounce
            self.ev_click.clear()
            self.onclick()
