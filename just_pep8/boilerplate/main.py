import asyncio
import sys
import test

def _handle_exception(loop, context):
    print('\nGlobal exception handler')
    sys.print_exception(context['exception'])
    sys.exit()

def main(app):
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)
    app.main()
    loop.run_forever()

try:
    app = test.MyTestApp()
    print('Running the main loop, press Ctrl-C to stop')
    asyncio.run(main(app))
except KeyboardInterrupt:
    print('\nStopped')
finally:
    asyncio.new_event_loop()
    app.deinit()
