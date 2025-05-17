import asyncio

class MyDemoBlinkingLED:
    _state = False
    _blinking = False

    send = lambda topic, payload: None

    def recv(self, topic, payload):
        if topic == b'/set':
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
            self.send(b'', b'1' if self._state else b'0')

class App:
    _jobs = {}
    _dots = False

    def __init__(self, root_prefix):
        self._root_prefix = root_prefix

    def add_job(self, prefix, job):
        prefix = self._root_prefix + b'/' + prefix
        job.send = self._send_callback(prefix)
        self._jobs[prefix] = job

    async def _tick(self):
        while True:
            print('.', end='', flush=True)
            self._dots = True
            await asyncio.sleep(.1)

    def _clean(self):
        if self._dots:
            print('')
            self._dots = False

    async def _bomb(self):
        await asyncio.sleep(1)
        self._mqtt_recv(b'dev/board99/gpio13/set', b'1')
        await asyncio.sleep(2)
        self._mqtt_recv(b'dev/board99/gpio13/set', b'0')
        await asyncio.sleep(1)
        1/0

    async def main(self):
        asyncio.create_task(self._bomb())
        for prefix in self._jobs:
            asyncio.create_task(self._jobs[prefix].main())
        await self._tick()

    def _mqtt_recv(self, topic, payload):
        self._clean()
        print('[MQTT recv]', topic.decode(), payload.decode())
        for prefix in self._jobs:
            if topic.startswith(prefix):
                self._jobs[prefix].recv(topic[len(prefix)::], payload)

    def _mqtt_send(self, topic, payload):
        self._clean()
        print('[MQTT send]', topic.decode(), payload.decode())
        self._mqtt_recv(topic, payload) # if subscribed to all

    def _send_callback(self, topic):
        return lambda suffix, payload: self._mqtt_send(topic + suffix, payload)

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
    app = App(b'dev/board99')
    app.add_job(b'gpio13', MyDemoBlinkingLED())
    #app.add_job(b'gpio9', MyDemoBlinkingLED())
    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(main(app))
except KeyboardInterrupt:
    print('\nStopped')
except asyncio.exceptions.CancelledError:
    pass
finally:
    asyncio.new_event_loop()
