import gc
print('Free memory:', gc.mem_free())

import asyncio
import sys
import app

def _handle_exception(loop, context):
    print('\nGlobal exception handler')
    sys.print_exception(context['exception'])
    sys.exit()

def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)
    await app.main()

try:
    app.init()
    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(main())
except KeyboardInterrupt:
    print('\nStopped')
finally:
    asyncio.new_event_loop()
    app.deinit()
    print('Free memory:', gc.mem_free())
