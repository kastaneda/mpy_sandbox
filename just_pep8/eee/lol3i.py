import asyncio

class BaseHandler:
    def __init__(self, broker, topic_prefix: str='#'):
        self.broker = broker
        self.topic_prefix = topic_prefix
        broker.subscribe(self)

    async def main(self):
        pass

    def handle(self, topic_suffix: str, payload: str):
        pass

    def send(self, topic_suffix: str, payload: str):
        topic = self.topic_prefix + topic_suffix
        self.broker.send(topic, payload)

class MyDemoBlinkingLED(BaseHandler):
    _state = False
    _blinking = False

    def __init__(self, broker, topic_prefix: str, gpio: int):
        super().__init__(broker, topic_prefix)
        # self._pin = machine.Pin(gpio, machine.OUT) 

    def handle(self, topic_suffix: str, payload: str):
        if topic_suffix == '/set':
            self._blinking = bool(int(payload))

    async def main(self):
        while True:
            await asyncio.sleep(.5)
            self._set_state(self._blinking)
            await asyncio.sleep(.5)
            self._set_state(False)

    def _set_state(self, new_state):
        if self._state != new_state:
            #self._pin.value(int(new_state))
            self._state = new_state
            self.send('', '1' if self._state else '0')
            print('1' if self._state else '0', end='', flush=True)

class MyDemoPlan(BaseHandler):
    async def main(self):
        await asyncio.sleep(.5)
        self.broker.send('led13/set', '1')
        await asyncio.sleep(3)
        self.broker.send('led13/set', '0')

class TickingDots(BaseHandler):
    async def main(self):
        global debug_dots
        while True:
            print('.', end='', flush=True)
            debug_dots = True
            await asyncio.sleep(.1)

class TickingBomb(BaseHandler):
    async def main(self):
        await asyncio.sleep(5)
        1/0

class App:
    def __init__(self, global_prefix: str=''):
        self.handlers = []
        self.global_prefix = global_prefix

    def subscribe(self, handler: BaseHandler):
        self.handlers.append(handler)

    async def main(self):
        jobs = [h.main() for h in self.handlers]
        try:
            await asyncio.gather(*jobs)
        except Exception as e:
            print('', e, sep='\n')

    def handle(self, topic: str, payload: str):
        if topic.startswith(self.global_prefix):
            topic = topic[len(self.global_prefix):]
            for handler in self.handlers:
                if topic.startswith(handler.topic_prefix):
                    topic_suffix = topic[len(handler.topic_prefix):]
                    handler.handle(topic_suffix, payload)

    def send(self, topic: str, payload: str):
        topic = self.global_prefix + topic
        self.handle(topic, payload)

def _handle_exception(loop, context):
    print('\nGlobal exception handler')
    print(context['exception'])
    #loop.stop()
    tasks = asyncio.all_tasks(loop)
    for task in tasks:
        task.cancel()

async def main(app):
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)
    await app.main()

try:
    app = App('dev/board99/')
    MyDemoBlinkingLED(app, 'led13', 13)
    MyDemoPlan(app)
    TickingDots(app)
    TickingBomb(app)

    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(main(app))
except KeyboardInterrupt:
    print('\nStopped')
except asyncio.exceptions.CancelledError:
    pass
finally:
    asyncio.new_event_loop()
