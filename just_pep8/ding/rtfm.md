```
         ___                  ___ _
        |   \ ___ _ __  ___  | __(_)_ _ _ ____ __ ____ _ _ _ ___
        | |) / -_) '  \/ _ \ | _|| | '_| '  \ V  V / _` | '_/ -_)
======= |___/\___|_|_|_\___/ |_| |_|_| |_|_|_\_/\_/\__,_|_| \___| ======
------------------------------------------------------------------------
```

Files
-----

 - `boot.py`: executed on every boot, low-level things
 - `main.py`: executed after `boot.py`, runs `app.py`
 - `cfg.py`:  configuration, especially for the Wi-Fi
 - `link.py`: utility module to connect to the Wi-Fi
 - `app.py`:  main application logic and MQTT glue code
 - `demo.py`: the actual firmware payload, to blink the LED
 - `ding.py`: the bonus track of the firmware, a button handler
 - `dbg.py`:  helper utility, reports memory status
