import time, network, machine, urequests, json
from myConfig import *

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

def loadRTC():
    try:
        data = json.loads(rtc.memory())
        print('RTC memory:', data)
        for key in data:
            globals()[key] = data[key]
    except:
        print('RTC memory not loaded')
        pass

def saveRTC():
    global myEndpoint
    rtc.memory(json.dumps({
        'myEndpoint': myEndpoint
    }))

def waitForWifi(dots = 40):
    for i in range(dots):
        print('.', end='')
        time.sleep_ms(250)
        if sta_if.isconnected():
            print(' connected')
            return True
    print(' not connected')
    return False

def setupWifi():
    global myEndpoint
    sta_if.scan()
    for tryWifi in myWifiConfig:
        print('Connecting to', tryWifi['essid'], '', end='')
        sta_if.connect(tryWifi['essid'], tryWifi['password'])
        if waitForWifi():
            myEndpoint = tryWifi['endpoint']
            saveRTC()
            return True
    print('Wi-Fi setup failed')
    myEndpoint = False
    saveRTC()
    return False

def check():
    if sta_if.isconnected():
        print('Connected to Wi-Fi')
    else:
        print('Not connected to Wi-Fi')
        setupWifi()
    print(sta_if.ifconfig())
 
def deep(sleepSeconds=10):
    print('Go to deep sleep for', sleepSeconds, 'seconds')
    saveRTC()
    rtc.alarm(rtc.ALARM0, sleepSeconds * 1000)
    machine.deepsleep()

def demo():
    if not myEndpoint:
        print('No endpoint defined')
        return
    print(urequests.get(url=myEndpoint).content)

print('\n\nHello world!')
loadRTC()
check()
demo()

