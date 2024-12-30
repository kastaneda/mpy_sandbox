#!/usr/bin/python3

import asyncio
import aiohttp

async def send_request():
    async with aiohttp.ClientSession() as session:
        print("Sending HTTP request...")
        #url = "https://jsonplaceholder.typicode.com/posts/1"
        url = "http://192.168.0.34/hello_ssd1306.php"
        async with session.get(url) as response:
            data = await response.text()
            print("Response received:", data)

async def progress_indicator():
    try:
        while True:
            print(".", end="", flush=True)
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("\nProgress indicator stopped.")

async def main():
    # Create tasks for both coroutines
    request_task = asyncio.create_task(send_request())
    progress_task = asyncio.create_task(progress_indicator())

    # Wait for the request task to finish
    await request_task

    # Cancel the progress indicator task
    progress_task.cancel()

    # Wait for the progress task to finish cleanup
    await progress_task

# Run the event loop
asyncio.run(main())
