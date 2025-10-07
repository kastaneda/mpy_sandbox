import asyncio

async def print_dots():
    try:
        while True:
            print('.', end='', flush=True)
            await asyncio.sleep(.25)
    except asyncio.CancelledError:
        print('')

async def long_calc():
    for i in range(3):
        print(i, end='', flush=True)
        await asyncio.sleep(1)
    return 321

async def main():
    dots_task = asyncio.create_task(print_dots())
    result = await long_calc()
    dots_task.cancel()
    return result

print(asyncio.run(main()))
