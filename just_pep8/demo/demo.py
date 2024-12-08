import asyncio
import machine

def init(callback):
    global led, pub
    led = machine.Pin(2, machine.Pin.OUT)
    led.value(1)
    pub = callback

async def blink():
    while True:
        led.value(0)
        pub(b'1')
        await asyncio.sleep_ms(500)

        led.value(1)
        pub(b'0')
        await asyncio.sleep_ms(500)
