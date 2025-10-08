import asyncio

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
    def __init__(self, name):
        self.name = name
        self.is_blinking = False
        self.value = False

    def set_value(self, app, value):
        if value != self.value:
            self.value = value
            app.handle(self.name, int(value))

    async def main(self, app):
        while True:
            await asyncio.sleep(.5)
            self.set_value(app, self.is_blinking)
            await asyncio.sleep(.5)
            self.set_value(app, False)

    def handle(self, topic, payload):
        if topic == self.name+'/set':
            self.is_blinking = bool(int(payload))

class TickingBomb:
    async def main(self, app):
        await asyncio.sleep(2)
        app.handle('led13/set', 1)
        await asyncio.sleep(3)
        app.handle('led13/set', 0)
        await asyncio.sleep(3)
        1/0

class DebugDots:
    dots = False

    async def main(self, app):
        print('Main loop started, press Ctrl-C to stop')
        try:
            while True:
                await asyncio.sleep(.1)
                print('.', end='', flush=True)
                self.dots = True
        except asyncio.CancelledError:
            if self.dots:
                print()
            print('Main loop stopped')

    def handle(self, topic, payload):
        if self.dots:
            print()
            self.dots = False
        print(topic, payload)

try:
    app = App()
    app.add(BlinkingLED('led13'))
    app.add(TickingBomb())
    app.add(DebugDots())
    asyncio.run(app.main())
except KeyboardInterrupt:
    print('Stopped')
