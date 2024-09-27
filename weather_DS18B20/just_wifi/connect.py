import config, time, network, machine, json

debug_print = print if config.debug else lambda *args, **kwargs: None
sta_if = network.WLAN(network.STA_IF)
rtc = machine.RTC()
rtcm = {}

def connected():
    global sta_if
    return sta_if.isconnected()

def wifi(key=None):
    global rtcm
    try:
        wifi = rtcm['wifi']
        return wifi[key] if key else wifi
    except KeyError:
        return False

def loadRTC():
    global rtcm
    try:
        rtcm = json.loads(rtc.memory())
        debug_print('RTC memory:', rtcm)
    except ValueError:
        debug_print('RTC memory not loaded')
        pass

def saveRTC():
    global rtcm
    rtc.memory(json.dumps(rtcm))    

def fixBuggyDHCP():
    global sta_if
    cfg = sta_if.ifconfig()
    sta_if.ifconfig((cfg[0], cfg[1], cfg[2], '8.8.8.8'))

def tryWifi(candidate):
    global sta_if
    debug_print('Connecting to', candidate['essid'], '', end='')
    sta_if.connect(candidate['essid'], candidate['password'])
    for i in range(40):
        if config.debug:
            debug_print('.', end='')
        time.sleep_ms(250)
        if connected():
            debug_print(' connected')
            return True
    debug_print(' not connected')
    return False

def setupWifi():
    global sta_if, rtcm
    sta_if.active(True)
    if connected() and wifi():
        fixBuggyDHCP()
        debug_print('Already connected to Wi-Fi')
        return True
    sta_if.scan()
    lastWifi = wifi()
    if lastWifi:
        if tryWifi(lastWifi):
            fixBuggyDHCP()
            rtcm['wifi'] = lastWifi
            saveRTC()
            return True
    for candidate in config.wifi_avail:
        if lastWifi != candidate and tryWifi(candidate):
            fixBuggyDHCP()
            rtcm['wifi'] = candidate
            saveRTC()
            return True
    debug_print('Wi-Fi setup failed')
    rtcm['wifi'] = False
    saveRTC()
    return False

def deepsleep(seconds=60):
    global rtc
    saveRTC()
    debug_print('Go to deep sleep for', seconds, 'seconds')
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, seconds * 1000)
    machine.deepsleep()
