import machine, time, umqtt.robust, asyncio, gc
import config, connect, shift_stepper

connect.load_rtc()
connect.setup_wifi()

# See adc_mode.py
vcc = machine.ADC(1)

# WeMos board: D4 (GPIO2), onboard LED
led = machine.Pin(2, machine.Pin.OUT)
led.value(1)

# WeMos board: D3 (GPIO0)
sg90 = machine.PWM(machine.Pin(0, mode=machine.Pin.OUT))

shift_stepper.set_direction(config.stepper_direction)
shift_stepper.load_position(connect.rtcm.get('motor'))

# The only one background job that really needs timer
stepper_timer = machine.Timer(-1)
stepper_timer.init(
    callback=lambda t: shift_stepper.one_step(),
    freq=400,
    mode=machine.Timer.PERIODIC
)

def topic(suffix):
    return (config.board_id + '/' + suffix).encode('ascii')

# The onboard LED is inverted: value(0) means ON, 1 means OFF
# It's more practical to invert it here, on the device's side
def report_led():
    client.publish(topic('led'), str(1-led.value()))

recent_reports = {}
def report_changed(name, value):
    global recent_reports
    if recent_reports.get(name, False) != value:
        client.publish(topic(name), str(value))
        recent_reports[name] = value

async def every_100ms():
    while True:
        report_changed('motor1', shift_stepper.motor1.step_actual)
        report_changed('motor2', shift_stepper.motor2.step_actual)
        report_changed('motor3', shift_stepper.motor3.step_actual)
        connect.rtcm.update(motor=shift_stepper.save_position())
        await asyncio.sleep_ms(100)

async def every_1s():
    while True:
        client.ping()
        print('.', end='')
        await asyncio.sleep(1)

async def every_20s():
    while True:
        report_led()
        client.publish(topic('status'), b'1')
        client.publish(topic('vcc'), str(vcc.read()))
        client.publish(topic('motor1'), str(shift_stepper.motor1.step_actual))
        client.publish(topic('motor2'), str(shift_stepper.motor2.step_actual))
        client.publish(topic('motor3'), str(shift_stepper.motor3.step_actual))
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        await asyncio.sleep(20)

async def mqtt_loop():
    while True:
        client.check_msg()
        await asyncio.sleep(0)

async def led_blink(times):
    for i in range(times * 2):
        led.value(1 - led.value())
        report_led()
        await asyncio.sleep_ms(250)

task_led_blink = None
def start_led_blink(times):
    global task_led_blink
    if task_led_blink:
        task_led_blink.cancel()
    task_led_blink = asyncio.create_task(led_blink(int(times)))

async def move_servo(u16):
    try:
        sg90.init(freq=50, duty_u16=u16)
        await asyncio.sleep_ms(500)
    except asyncio.CancelledError:
        print('X', end='')
        raise
    finally:
        sg90.deinit()

task_move_servo = None
def start_move_servo(u16):
    global task_move_servo
    if task_move_servo:
        task_move_servo.cancel()
    task_move_servo = asyncio.create_task(move_servo(int(u16)))

topic_callbacks = {
    topic('led/set'): lambda m: led.value(0 if m == b'1' else 1),
    topic('motor1/set'): shift_stepper.motor1.target,
    topic('motor2/set'): shift_stepper.motor2.target,
    topic('motor3/set'): shift_stepper.motor3.target,
    topic('sleep/set'): connect.deep_sleep,
    #topic('led_blink/set'): lambda m: asyncio.create_task(led_blink(int(m))),
    topic('led_blink/set'): start_led_blink,
    #topic('servo/set'): lambda m: asyncio.create_task(move_servo(int(m))),
    topic('servo/set'): start_move_servo,
}

def mqtt_callback(topic_name, msg):
    fn = topic_callbacks.get(topic_name, lambda x: None)
    fn(msg)

# https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/README.rst
# keepalive=1 is VERY small period; for real life it should be >= 5 sec
client = umqtt.robust.MQTTClient(config.board_id, connect.wifi('mqtt'), keepalive=1)
client.set_last_will(topic('status'), b'0')
client.connect()
client.publish(topic('status'), b'1')

client.set_callback(mqtt_callback)
client.subscribe(topic('+/set'))

async def main():
    asyncio.create_task(every_100ms())
    asyncio.create_task(every_1s())
    asyncio.create_task(every_20s())
    asyncio.create_task(mqtt_loop())
    asyncio.get_event_loop().run_forever()

try:
    print('Start MQTT main loop, press Ctrl-C to stop')
    asyncio.run(main())
except KeyboardInterrupt:
    print('\nStopped')
finally:
    stepper_timer.deinit()
    connect.save_rtc()
    client.disconnect()
    asyncio.new_event_loop()
