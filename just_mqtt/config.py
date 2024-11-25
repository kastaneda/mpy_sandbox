debug = True
#debug = False

board_id = 'board05'

wifi_avail = [
    {
        'essid': 'equinox',
        'password': '...',
        'mqtt': '192.168.0.82'
    },
#    {
#        'essid': 'Termux',
#        'password': '...',
#    },
    {
        'essid': 'sensors',
        'password': '...',
        'dns': '8.8.8.8',
        'mqtt': '192.168.0.82'
    }
]

stepper_reverse = {
    'motor1': True,
    'motor2': False,
    'motor3': False
}
