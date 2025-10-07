import asyncio

class App:
    jobs = []

    def __init__(self, name):
        self.name = name
        self.send('App.init()')

    def send(self, *args, **kwargs):
        pass

    async def main(self):
        self.send('App.main()')
        jobs = [job.main(app) for job in self.jobs]
        await asyncio.gather(*jobs)

class BlinkingLED:
    def __init__(self, name):
        self.name = name

    async def main(self, app):
        app.send(self.name, 'BlinkingLED.main()')
        while True:
            await asyncio.sleep(1)
            app.send(self.name, 'value=1')
            await asyncio.sleep(1)
            app.send(self.name, 'value=0')

class TickingBomb:
    async def main(self, app):
        app.send('[no name]', 'TickingBomb.main()')
        await asyncio.sleep(5)
        1/0

class AppDebug(App):
    def __init__(self, *args, **kwargs):
        self._debug = DebugDots()
        self.jobs.append(self._debug)
        super().__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        self._debug.print(self.name, *args, **kwargs)

    async def main(self):
        try:
            await super().main()
        except Exception as e:
            self._debug.print(e)

class DebugDots:
    _dots = False

    async def main(self, app):
        app.send('[no name]', 'Debugger.main()')
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
    app.jobs.append(BlinkingLED('led13'))
    app.jobs.append(TickingBomb())
    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(app.main())
except KeyboardInterrupt:
    print('\nStopped')
