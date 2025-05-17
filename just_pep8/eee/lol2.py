import asyncio

debug_dots = False

def debug_dots_clean():
    global debug_dots
    if debug_dots:
        print('')
        debug_dots = False

class MessageBroker:
    def __init__(self, global_prefix = ''):
        self.handlers = []
        self.global_prefix = global_prefix

    def subscribe(self, handler):
        self.handlers.append(handler)

    def handle(self, topic: str, payload: str):
        debug_dots_clean()
        print('[Message from MQTT broker]', topic, payload)
        if topic.startswith(self.global_prefix):
            topic = topic[len(self.global_prefix):]
            for handler in self.handlers:
                if topic.startswith(handler.topic_prefix):
                    topic_suffix = topic[len(handler.topic_prefix):]
                    handler.handle(topic_suffix, payload)

    def send(self, topic: str, payload: str):
        topic = self.global_prefix + topic
        debug_dots_clean()
        print('[Message to MQTT broker]', topic, payload)
        self.handle(topic, payload)

class BaseJob:
    async def main(self):
        raise NotImplementedError

class BaseHandler:
    def __init__(self, broker: MessageBroker, topic_prefix: str):
        self.broker = broker
        self.topic_prefix = topic_prefix
        broker.subscribe(self)

    def handle(self, topic_suffix: str, payload: str):
        raise NotImplementedError

    def send(self, topic_suffix: str, payload: str):
        topic = self.topic_prefix + topic_suffix
        self.broker.send(topic, payload)

class MyDemoBlinkingLED(BaseHandler, BaseJob):
    _state = False
    _blinking = False

    def __init__(self, broker: MessageBroker, topic_prefix: str, gpio: int):
        super().__init__(broker, topic_prefix)
        debug_dots_clean()
        print('[MyDemoBlinkingLED] Init GPIO', gpio)
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

class MyDemoPlan(BaseHandler, BaseJob):
    def handle(self, topic_suffix: str, payload: str):
        pass

    async def main(self):
        await asyncio.sleep(2)
        self.broker.send('led13/set', '1')
        await asyncio.sleep(2)
        self.broker.send('led13/set', '0')

class TickingDots(BaseJob):
    async def main(self):
        global debug_dots
        while True:
            print('.', end='', flush=True)
            debug_dots = True
            await asyncio.sleep(.1)

class TickingBomb(BaseJob):
    async def main(self):
        await asyncio.sleep(8)
        1/0

class App:
    jobs = []

    def add_job(self, job):
        self.jobs.append(job)

    async def main(self):
        for job in self.jobs:
            asyncio.create_task(job.main())
        ticking = TickingDots()
        await ticking.main()

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
    broker = MessageBroker('dev/board99/')
    led13 = MyDemoBlinkingLED(broker, 'led13', 13)
    plan = MyDemoPlan(broker, 'xxxxx')
    bomb = TickingBomb()

    app = App()
    app.add_job(led13)
    app.add_job(plan)
    app.add_job(bomb)

    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(main(app))
except KeyboardInterrupt:
    print('\nStopped')
except asyncio.exceptions.CancelledError:
    pass
finally:
    asyncio.new_event_loop()
