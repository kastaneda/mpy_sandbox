import config, time, network, machine, json, uos

print = print if config.debug else lambda *args, **kwargs: None
sta_if = network.WLAN(network.STA_IF)
rtc = machine.RTC()
rtcm = {}

def connected():
    return sta_if.isconnected()

def wifi(key=None):
    return rtcm.get('wifi', {}).get(key) if key else rtcm.get('wifi')

def load_rtc():
    global rtcm
    try:
        rtcm = json.loads(rtc.memory())
        print('RTC memory:', rtcm)
    except ValueError:
        print('RTC memory not loaded')

def save_rtc():
    rtc.memory(json.dumps(rtcm))

def try_wifi(candidate):
    print('Connecting to', candidate['essid'], '', end='')
    sta_if.connect(candidate['essid'], candidate['password'])
    for i in range(40):
        print('.', end='')
        time.sleep_ms(250)
        if connected():
            print(' connected')
            if 'dns' in candidate:
                cfg = sta_if.ifconfig()
                print('DNS override from', cfg[3], 'to', candidate['dns'])
                sta_if.ifconfig((cfg[0], cfg[1], cfg[2], candidate['dns']))
            print(sta_if.ifconfig())
            return True
    print(' not connected')
    return False

def setup_wifi():
    global rtcm
    sta_if.active(True)
    if connected() and wifi():
        print('Wi-Fi already configured')
        print(sta_if.ifconfig())
        return True
    sta_if.scan()
    last_wifi = wifi()
    if last_wifi:
        if try_wifi(last_wifi):
            return True
    for candidate in config.wifi_avail:
        if last_wifi != candidate and try_wifi(candidate):
            rtcm['wifi'] = candidate
            save_rtc()
            return True
    print('Wi-Fi setup failed')
    sta_if.active(False)
    rtcm['wifi'] = False
    save_rtc()
    return False

def deep_sleep(seconds=60):
    save_rtc()
    print('Go to deep sleep for', int(seconds), 'seconds')
    sysname = uos.uname().sysname
    if sysname == 'esp32':
        machine.deepsleep(int(seconds) * 1000)
    elif sysname == 'esp8266':
        rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
        rtc.alarm(rtc.ALARM0, int(seconds) * 1000)
        machine.deepsleep()
    else:
        raise Exception('Platform not supported')
