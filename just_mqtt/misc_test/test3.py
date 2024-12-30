#!/usr/bin/python3

import asyncio

async def print_a():
    while True:
        print("A")
        await asyncio.sleep(1)

async def print_b():
    while True:
        print("B")
        await asyncio.sleep(1)

async def main():
    # Create tasks for both coroutines
    task_a = asyncio.create_task(print_a())
    task_b = asyncio.create_task(print_b())

    # Run for 5 seconds
    await asyncio.sleep(5)

    # Cancel tasks after timeout
    task_a.cancel()
    task_b.cancel()

    # Wait for tasks to finish cleanup
    await asyncio.gather(task_a, task_b, return_exceptions=True)

# Run the event loop
asyncio.run(main())
