#!/usr/bin/python3 -u
import asyncio
import sys
import test

def _handle_exception(loop, context):
    print('\nGlobal exception handler')
    print(context['exception'])
    loop.stop()
    #sys.exit()

async def main(app):
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)
    await app.main()

try:
    app = test.MyTestApp()
    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(main(app))
except KeyboardInterrupt:
    print('\nStopped')
except RuntimeError:
    # RuntimeError: Event loop stopped before Future completed
    pass
finally:
    asyncio.new_event_loop()
    app.deinit()
