Quick notes:

import cfg, link
link.up(cfg.wifi)

###

import network
wlan = network.WLAN(network.STA_IF)

# Scan and sort by RSSI desc
avail = wlan.scan()
avail.sort(key=lambda x: -x[3])
for net in avail:
    print(net)

# Print status
stat_names = {
    network.STAT_IDLE: 'STAT_IDLE',
    network.STAT_CONNECTING: 'STAT_CONNECTING',
    network.STAT_WRONG_PASSWORD: 'STAT_WRONG_PASSWORD',
    network.STAT_NO_AP_FOUND: 'STAT_NO_AP_FOUND',
    network.STAT_CONNECT_FAIL: 'STAT_CONNECT_FAIL',
    network.STAT_GOT_IP: 'STAT_GOT_IP',
}
print('wlan.status() =', stat_names[wlan.status()])
