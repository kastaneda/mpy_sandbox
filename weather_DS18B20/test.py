import time, network, ntptime

print(time.localtime())

t_start = time.ticks_ms()
#print('t_start =', t_start)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.ifconfig(('192.168.0.114', '255.255.255.0', '192.168.0.1', '192.168.0.1'))

if not sta_if.isconnected():
    sta_if.connect('...', '...')
    while True:
        print('Connecting...')
        if (sta_if.isconnected()):
            break
        time.sleep_ms(250)

print('Connected')

print(sta_if.ifconfig())

t_end = time.ticks_ms()
#print('t_end =', t_end)

delta = time.ticks_diff(t_end, t_start)
print('Connection time =', delta, 'ms')

ntptime.settime()
print(time.localtime())

time.sleep_ms(10000)
sta_if.active(False)

