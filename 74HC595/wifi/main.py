import myStepper, time, network
from myConfig import *

def setupWifi():
    global sta_if, myEndpoint
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.scan()
    for tryWifi in myWifiConfig:
        print('Connecting to', tryWifi['essid'], '', end='')
        sta_if.connect(tryWifi['essid'], tryWifi['password'])
        for i in range(40):
            print('.', end='')
            if (sta_if.isconnected()):
                print(' connected!')
                myEndpoint = tryWifi['endpoint']
                return True
            time.sleep_ms(250)
        print(' not connected')
    print('Wi-Fi setup failed')

setupWifi()
print('Endpoint:', myEndpoint)

'''
print('OK LOL')

myStepper.motor1.target(1024)
for x in range(770):
    myStepper.oneStep()
    time.sleep_ms(3)

myStepper.motor2.target(1024)
for x in range(770):
    myStepper.oneStep()
    time.sleep_ms(3)

myStepper.motor3.target(1024)
for x in range(1026):
    myStepper.oneStep()
    time.sleep_ms(3)

print('Done')
'''


