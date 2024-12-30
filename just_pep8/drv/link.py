import network

wlan = network.WLAN(network.STA_IF)
ssid = None

def up(cfg_wifi=None, last_ssid=None):
    global ssid
    if cfg_wifi == None:
        return wlan.isconnected()

    wlan.active(True)
    if last_ssid:
        if try_wifi(cfg_wifi[last_ssid]):
            return True
    ssid_skip = [last_ssid]

    net_avail = wlan.scan()
    net_avail.sort(key=lambda x: -x[3])     # Sort by RSSI descending
    for net in net_avail:
        ssid = net[0]
        if ssid in cfg_wifi and ssid not in ssid_skip:
            ssid_skip.append(ssid)
            if try_wifi(ssid, cfg_wifi[ssid]):
                return True

    for ssid in cfg_wifi:                   # Try everything else
        if ssid not in ssid_skip:
            if try_wifi(ssid, cfg_wifi[ssid]):
                return True

    ssid = None
    return False

def try_wifi(ssid, opt):
    #print('Connecting to Wi-Fi', ssid, '... ', end='')
    wlan.connect(ssid, opt.get('pwd', ''))
    while True:
        st = wlan.status()

        if st == network.STAT_CONNECTING:
            continue

        if st == network.STAT_GOT_IP:
            #print('Connected')
            #print(wlan.ifconfig())
            if 'dns' in opt:
                ifcfg = wlan.ifconfig()
                #print('Override DNS from', ifcfg[3], 'to', opt['dns'])
                wlan.ifconfig((ifcfg[0], ifcfg[1], ifcfg[2], opt['dns']))
            return True

        #if st == network.STAT_NO_AP_FOUND:
        #    print('AP not found')
        #elif st == network.STAT_WRONG_PASSWORD:
        #    print('Wrong password')
        #else:
        #    print('Connection failed')
        wlan.disconnect()
        return False
