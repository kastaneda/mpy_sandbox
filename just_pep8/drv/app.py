import asyncio
import cfg
import dbg
import demo
import ding
import drv
import dsrv
import link
import umqtt.simple

def init():
    global mq, led, btn, sg90
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

    led = demo.MyDemoLED(2, pub_to(b'led'), 0, 1) # pin D4, built-in LED
    btn = ding.MyDingDong(0, led.toggle_blink) # pin D3
    dbg.init(pub_to(b'mem_free'))
    drv.init()
    sg90 = dsrv.MyDelayServo(4) # pin D2

async def tick():
    while True:
        mq.ping()
        print('.', end='')
        await asyncio.sleep(1)

async def drv_report(motor, pub):
    reported = None
    skip_count = 0
    while True:
        if motor.actual != reported:
            reported = motor.actual
            pub(reported)
            skip_count = 0
        else:
            skip_count += 1
            if skip_count > 150:
                pub(reported)
                skip_count = 0
        await asyncio.sleep_ms(100)

async def main():
    asyncio.create_task(mqtt_loop())
    asyncio.create_task(dbg.main())
    asyncio.create_task(led.main())
    asyncio.create_task(btn.main())
    asyncio.create_task(drv_report(drv.m1, pub_to('motor1')))
    asyncio.create_task(drv_report(drv.m2, pub_to('motor2')))
    asyncio.create_task(drv_report(drv.m3, pub_to('motor3')))
    asyncio.create_task(sg90.main())
    await tick()

def mqtt_callback(t, msg):
    if t == topic(b'led/set'):
        led.set_value(msg)
    if t == topic(b'led_blink/set'):
        led.set_blink(msg)
    if t == topic(b'motor1/set'):
        drv.m1.go(msg)
    if t == topic(b'motor2/set'):
        drv.m2.go(msg)
    if t == topic(b'motor3/set'):
        drv.m3.go(msg)
    if t == topic(b'servo/set'):
        sg90.go(msg)

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
    if drv.tim:
        drv.deinit()
    if mq and mq.sock:
        print('Disconnecting from MQTT broker')
        mq.sock.close()

mq = None
