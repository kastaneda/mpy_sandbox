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

class DebugPrint:
    dots = False

    async def main(self, app):
        print('Main loop started, press Ctrl-C to stop')
        while True:
            await asyncio.sleep_ms(500)
            print('.', end='')
            self.dots = True

    def handle(self, topic, payload):
        if self.dots:
            print()
            self.dots = False
        print(topic, payload)

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

import network
import umqtt.simple
class WirelessMQTT:
    def __init__(self, server, prefix, **kwargs):
        self.wlan = network.WLAN(network.STA_IF)
        self.prefix = prefix+'/'
        kwargs['keepalive'] = 2
        self.mq = umqtt.simple.MQTTClient(prefix, server, **kwargs)
        self.mq.set_last_will(self.prefix+'online', b'0', retain=True)
        self.mq.set_callback(self.mqtt_callback)
        self.nodup_t = self.nodup_p = None

    async def main(self, app):
        self.app = app
        while not self.wlan.isconnected():
            await asyncio.sleep(0)
        self.mq.connect()
        self.mq.publish(self.prefix+'online', b'1', retain=True)
        self.mq.subscribe(self.prefix+'+/set')
        await asyncio.gather(self.ping(), self.check_msg())

    async def ping(self):
        while True:
            self.mq.ping()
            await asyncio.sleep(1)

    async def check_msg(self):
        while True:
            self.mq.check_msg()
            await asyncio.sleep(0)

    def mqtt_callback(self, topic, payload):
        topic, payload = topic.decode(), payload.decode()
        if topic.startswith(self.prefix):
            topic = topic[len(self.prefix):]
            self.nodup_t, self.nodup_p = topic, payload
            self.app.handle(topic, payload)
        self.nodup_t = self.nodup_p = None

    def handle(self, topic, payload):
        if self.mq and self.mq.sock:
            if isinstance(payload, int):
                payload = str(payload)
            if topic != self.nodup_t or payload != self.nodup_p:
                self.mq.publish(self.prefix+topic, payload)

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

    # WeMos D1 mini, pin D4 = GPIO2, inverted (active-low)
    led = machine.Signal(2, machine.Pin.OUT, invert=True)
    app.add(BlinkingLED(led, 'led'))

    # WeMos D1 mini, pin D2 = GPIO4, pull-up (active-low)
    #btn = Signal(4, Pin.IN, Pin.PULL_UP, invert=True)
    btn = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
    app.add(SimpleButton(btn, 'btn', True))

    # Local connection: 'btn' -> 'led/set'
    app.add(LocalManager(app))

    # somewhere in 'boot.py':
    # import network
    # wlan = network.WLAN(network.STA_IF)
    # wlan.active(True)
    # if not wlan.isconnected():
    #     wlan.connect('ssid', 'password')
    app.add(WirelessMQTT('192.168.0.82', 'board99'))

    app.add(DebugPrint())
    app.add(DebugSpeed())
    app.add(DebugMem())
    asyncio.run(app.main())
except KeyboardInterrupt:
    print('Stopped')
