import config, connect, urequests

def demo():
    if connect.connected():
        endpoint = connect.wifi('endpoint')
        endpoint += '?board_id=' + config.board_id
        print(urequests.get(url=endpoint).content)

connect.loadRTC()
connect.setupWifi()
demo()

try:
    connect.rtcm['count'] += 1
except KeyError:
    connect.rtcm['count'] = 1

connect.saveRTC()
