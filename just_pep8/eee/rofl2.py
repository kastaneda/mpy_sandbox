import asyncio
import gc

class App:
    _jobs = []
    _handlers = []

    def __init__(self, name):
        self._prefix = name+'/'

    def add(self, obj):
        if hasattr(obj, 'main'):
            self._jobs.append(obj)
        if hasattr(obj, 'handle'):
            self._handlers.append(obj)

    def send(self, topic, payload):
        self.handle(self._prefix+topic, payload)

    async def main(self):
        jobs = [job.main(app) for job in self._jobs]
        await asyncio.gather(*jobs)

    def handle(self, topic, payload):
        if topic.startswith(self._prefix):
            topic = topic[len(self._prefix):]
            for handler in self._handlers:
                handler.handle(topic, payload)

class BlinkingLED:
    def __init__(self, name):
        self._name = name
        self._is_blinking = False
        self._value = False

    def _set_value(self, app, value):
        if value != self._value:
            self._value = value
            app.send(self._name, int(value))

    async def main(self, app):
        while True:
            await asyncio.sleep(.5)
            self._set_value(app, self._is_blinking)
            await asyncio.sleep(.5)
            self._set_value(app, False)

    def handle(self, topic, payload):
        if topic == self._name+'/set':
            self._is_blinking = bool(int(payload))

class TickingBomb:
    async def main(self, app):
        await asyncio.sleep(2)
        app.send('led13/set', 1)
        await asyncio.sleep(3)
        app.send('led13/set', 0)
        await asyncio.sleep(3)
        1/0

# class AppWifi(App):
#     ...
#
# class AppSerial(App):
#     ...

class AppDebug(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug = DebugDots()
        self.add(self._debug)

    def send(self, topic, payload):
        self._debug.print(self._prefix+topic, payload)
        super().send(topic, payload)

    async def main(self):
        try:
            await super().main()
        except Exception as e:
            self._debug.print(e)

class DebugDots:
    _dots = False

    async def main(self, app):
        while True:
            await asyncio.sleep(.1)
            print('.', end='', flush=True)
            self._dots = True

    def print(self, *args, **kwargs):
        if self._dots:
            print()
            self._dots = False
        print(*args, **kwargs)

try:
    app = AppDebug('board99')
    app.add(BlinkingLED('led13'))
    app.add(TickingBomb())
    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(app.main())
except KeyboardInterrupt:
    print('\nStopped')
