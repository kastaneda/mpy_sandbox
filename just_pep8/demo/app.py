import asyncio
import cfg
import link
import demo
import umqtt.simple

def init():
    global mq
    demo.init(pub_to('led'))

    if not link.up(cfg.wifi):
        raise RuntimeError('Cannot connect to Wi-Fi')

    print('Connecting to MQTT broker ... ', end='')
    mq = umqtt.simple.MQTTClient(
        cfg.board_id,
        cfg.wifi[link.ssid]['mqtt'],
        keepalive=2)
    mq.set_last_will(topic(b'status'), b'0')
    mq.connect()
    mq.publish(topic(b'status'), b'1')
    mq.set_callback(mqtt_callback)
    mq.subscribe(topic(b'+/set'))
    print('Connected')

async def tick():
    while True:
        mq.ping()
        print('.', end='')
        await asyncio.sleep(1)

async def bomb():
    await asyncio.sleep(5)
    1/0

async def main():
    asyncio.create_task(mqtt_loop())
    asyncio.create_task(demo.blink())
    asyncio.create_task(bomb())
    await tick()

def mqtt_callback(t, msg):
    # FIXME
    pass

async def mqtt_loop():
    while True:
        mq.check_msg()
        await asyncio.sleep(0)

def topic(suffix):
    return cfg.board_id + b'/' + suffix

def pub_to(suffix):
    t = topic(suffix)
    return lambda msg: mq.publish(t, msg)

def deinit():
    if mq and mq.sock:
        print('Disconnecting from MQTT broker')
        mq.sock.close()

mq = None
