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

class DebugDots:
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

class LocalManager:
    def __init__(self, app):
        self.app = app

    def handle(self, topic, payload):
        if topic == 'btn_D3':
            self.app.handle('led_D4/set', payload)

try:
    app = App()

    # WeMos D1 mini, pin D4 = GPIO2
    led = machine.Pin(2, machine.Pin.OUT)
    app.add(BlinkingLED(led, 'led_D4', True))

    # WeMos D1 mini, pin D3 = GPIO0
    btn = machine.Pin(0, machine.Pin.IN)
    app.add(SimpleButton(btn, 'btn_D3', True))

    app.add(DebugDots())
    app.add(LocalManager(app))
    asyncio.run(app.main())
except KeyboardInterrupt:
    print('Stopped')
