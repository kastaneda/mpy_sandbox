import asyncio
import machine

class App:
    tasks = []
    listeners = []

    def add(self, obj):
        if hasattr(obj, 'main'):
            self.tasks.append(obj)
        if hasattr(obj, 'handle'):
            self.listeners.append(obj)

    async def main(self):
        tasks = [task.main(self) for task in self.tasks]
        await asyncio.gather(*tasks)

    def handle(self, topic, payload):
        for listener in self.listeners:
            listener.handle(topic, payload)

class BlinkingLED:
    def __init__(self, gpio, name):
        self.gpio = gpio
        self.name = name
        self.name_set = name+'/set'
        self.is_blinking = False
        gpio.value(0)

    def set_value(self, app, value):
        value = int(value)
        if value != self.gpio.value():
            self.gpio.value(value)
            app.handle(self.name, value)

    async def main(self, app):
        while True:
            await asyncio.sleep_ms(75)
            self.set_value(app, self.is_blinking)
            await asyncio.sleep_ms(75)
            self.set_value(app, False)

    def handle(self, topic, payload):
        if topic == self.name_set:
            self.is_blinking = bool(int(payload))

class SimpleButton:
    def __init__(self, gpio, name, invert=False):
        self.gpio = gpio
        # Why? Because of this:
        # AttributeError: 'Signal' object has no attribute 'irq'
        if invert:
            self.gpio = machine.Signal(gpio, invert=True)
        self.name = name
        self.prev_state = -1
        self.ev_click = asyncio.Event()
        self.ev_click.set()
        gpio.irq(
            trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
            handler=self.click)

    def click(self, pin):
        self.ev_click.set()

    # TODO: add some debouncing
    async def main(self, app):
        while True:
            await self.ev_click.wait()
            self.ev_click.clear()
            state = self.gpio.value()
            if state != self.prev_state:
                app.handle(self.name, state)
                self.prev_state = state

class LocalManager:
    def __init__(self, app):
        self.app = app

    def handle(self, topic, payload):
        if topic == 'btn':
            self.app.handle('led/set', payload)

import sys
#import select
class StdioConnector:
    def __init__(self, prefix):
        self.prefix = prefix+'/'
        self.nodup_t = self.nodup_p = None

#    async def main(self, app):
#        poller = select.poll()
#        poller.register(sys.stdin, select.POLLIN)
#        while True:
#            res = poller.poll(0)
#            if res:
#                line = sys.stdin.readline().strip()
#                if line:
#                    topic, payload = line.split(' ', 1)
#                    if topic.startswith(self.prefix):
#                        topic = topic[len(self.prefix):]
#                        self.nodup_t, self.nodup_p = topic, payload
#                        app.handle(topic, payload)
#                        self.nodup_t = self.nodup_p = None
#            await asyncio.sleep(0)

    async def main(self, app):
        reader = asyncio.StreamReader(sys.stdin)
        while True:
            line = await reader.readline()
            if isinstance(line, bytes):
                line = line.decode()
            line = line.strip()
            if line:
                topic, payload = line.split(' ', 1)
                if topic.startswith(self.prefix):
                    topic = topic[len(self.prefix):]
                    self.nodup_t, self.nodup_p = topic, payload
                    app.handle(topic, payload)
                    self.nodup_t = self.nodup_p = None
    
    def handle(self, topic, payload):
        if topic != self.nodup_t or payload != self.nodup_p:
            print(self.prefix+topic, payload)

import time
class DebugSpeed:
    async def main(self, app):
        t0 = time.ticks_ms()
        loop_count = 0
        while True:
            loop_count = loop_count+1
            await asyncio.sleep(0)
            t1 = time.ticks_ms()
            delta = time.ticks_diff(t1, t0)
            if delta >= 10000:
                app.handle('loops', str(loop_count/10))
                loop_count = 0
                t0 = t1

import gc
class DebugMem:
    async def main(self, app):
        while True:
            await asyncio.sleep(5)
            gc.collect()
            app.handle('mem_free', gc.mem_free())

try:
    app = App()

    # Raspberry Pi Pico, built-in LED
    led = machine.Pin(25, machine.Pin.OUT)
    app.add(BlinkingLED(led, 'led'))

    # Raspberry Pi Pico, pin 15 = GPIO11
    btn = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)
    app.add(SimpleButton(btn, 'btn', True))

    # Local connection: 'btn' -> 'led/set'
    app.add(LocalManager(app))

    # https://test.de.co.ua/2024/02/20/arduino-mqtt.html
    # https://test.de.co.ua/2024/03/18/mqtt-oop.html
    app.add(StdioConnector('board98'))

    app.add(DebugSpeed())
    app.add(DebugMem())
    asyncio.run(app.main())
except KeyboardInterrupt:
    print('Stopped')
