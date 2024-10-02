import config, connect, machine, time, umqtt.robust

def t(suffix):
    return (config.board_id + '/' + suffix).encode('ascii')

connect.loadRTC()
connect.setupWifi()

# https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/README.rst
c = umqtt.robust.MQTTClient(config.board_id, connect.wifi('mqtt'), keepalive=3)
c.set_last_will(t('status'), b'0')
c.connect()
c.publish(t('status'), b'1')

led = machine.Pin(2, machine.Pin.OUT)
led.value(1)

def mqtt_callback(topic, msg):
    print('\nTopic:', topic, 'message:', msg)
    if topic == t('led/set'):
        led.value(1 if msg == b'1' else 0)

c.set_callback(mqtt_callback)
c.subscribe(t('+/set'))

print('MQTT main loop')
lastPingTime = time.ticks_ms()
while True:
    if c.check_msg() == None:
        time.sleep_ms(50)
    timeNow = time.ticks_ms()
    timeDiff = timeNow - lastPingTime
    if timeDiff > 500:
        lastPingTime = timeNow
        print('.', end='')
        c.ping()

