import asyncio
import cfg
import dbg
import demo
import ding
import link
import umqtt.simple

def init():
    global mq, led, btn
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

    led = demo.MyDemoLED(2, pub_to(b'led'), 0, 1)
    btn = ding.MyDingDong(0, led.toggle_blink)
    dbg.init(pub_to(b'mem_free'))

async def tick():
    while True:
        mq.ping()
        print('.', end='')
        await asyncio.sleep(1)

async def main():
    asyncio.create_task(mqtt_loop())
    asyncio.create_task(dbg.main())
    asyncio.create_task(led.main())
    asyncio.create_task(btn.main())
    await tick()

def mqtt_callback(t, msg):
    if t == topic(b'led/set'):
        led.set_value(msg)
    if t == topic(b'led_blink/set'):
        led.set_blink(msg)

async def mqtt_loop():
    while True:
        mq.check_msg()
        await asyncio.sleep(0)

def topic(suffix):
    return cfg.board_id + b'/' + suffix

def pub_to(suffix):
    t = topic(suffix)
    def pub(msg):
        if mq and mq.sock:
            mq.publish(t, str(msg))
    return pub

def deinit():
    if mq and mq.sock:
        print('Disconnecting from MQTT broker')
        mq.sock.close()

mq = None
