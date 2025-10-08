import asyncio
import machine
import sys
import select
import time
import gc

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
    def __init__(self, gpio, name, inverted=False):
        self.gpio = gpio
        self.name = name
        self.name_set = name+'/set'
        self.inverted = inverted
        self.is_blinking = False
        self.value = False
        gpio.value(int(inverted))

    def set_value(self, app, value):
        if value != self.value:
            self.value = value
            self.gpio.value(int(value ^ self.inverted))
            app.handle(self.name, int(value))

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
    def __init__(self, gpio, name, inverted=False):
        self.gpio = gpio
        self.name = name
        self.inverted = inverted
        self.prev_state = -1

    # TODO: add some debouncing
    async def main(self, app):
        while True:
            await asyncio.sleep(0)
            state = bool(self.gpio.value()) ^ self.inverted
            if state != self.prev_state:
                app.handle(self.name, int(state))
                self.prev_state = state

class StdioConnector:
    def __init__(self, prefix):
        self.prefix = prefix+'/'
        self.nodup_t = self.nodup_p = None

    async def main(self, app):
        poller = select.poll()
        poller.register(sys.stdin, select.POLLIN)
        while True:
            res = poller.poll(0)
            if res:
                line = sys.stdin.readline().strip()
                if line:
                    topic, payload = line.split(' ', 1)
                    if topic.startswith(self.prefix):
                        topic = topic[len(self.prefix):]
                        self.nodup_t, self.nodup_p = topic, payload
                        app.handle(topic, payload)
                        self.nodup_t = self.nodup_p = None
            await asyncio.sleep(0)
    
    def handle(self, topic, payload):
        if topic != self.nodup_t or payload != self.nodup_p:
            print(self.prefix+topic, payload)

class LolStats:
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

class LolMemStats:
    async def main(self, app):
        while True:
            await asyncio.sleep(5)
            gc.collect()
            app.handle('mem_free', gc.mem_free())

class LocalManager:
    def __init__(self, app):
        self.app = app

    def handle(self, topic, payload):
        if topic == 'btn':
            self.app.handle('led/set', payload)

try:
    app = App()

    # Raspberry Pi Pico, built-in LED
    led = machine.Pin(25, machine.Pin.OUT)
    app.add(BlinkingLED(led, 'led'))

    # Raspberry Pi Pico, pin 15 = GPIO11
    btn = machine.Pin(11, machine.Pin.IN, machine.Pin.PULL_UP)
    app.add(SimpleButton(btn, 'btn', True))

    # https://test.de.co.ua/2024/02/20/arduino-mqtt.html
    # https://test.de.co.ua/2024/03/18/mqtt-oop.html
    app.add(StdioConnector('board98'))

    app.add(LocalManager(app))
    app.add(LolStats())
    app.add(LolMemStats())
    asyncio.run(app.main())
except KeyboardInterrupt:
    print('Stopped')
