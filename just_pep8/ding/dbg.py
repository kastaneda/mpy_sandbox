import asyncio
import gc

def init(callback):
    global pub
    pub = callback

async def main():
    while True:
        pub(gc.mem_free())
        await asyncio.sleep(10)
