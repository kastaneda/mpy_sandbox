#!/usr/bin/python3 -u
import asyncio
import app

def _handle_exception(loop, context):
    print('\nGlobal exception handler')
    print(context['exception'])
    #loop.stop()
    tasks = asyncio.all_tasks(loop)
    for task in tasks:
        task.cancel()

async def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)
    await app.main()

try:
    app.init()
    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(main())
except KeyboardInterrupt:
    print('\nStopped')
except asyncio.exceptions.CancelledError:
    pass
finally:
    asyncio.new_event_loop()
    app.deinit()
