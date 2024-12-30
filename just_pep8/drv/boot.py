#import esp
#esp.osdebug(None)

#import os, machine
#os.dupterm(None, 1) # disable REPL on UART(0)

import gc
gc.collect()
print('Free memory:', gc.mem_free())

#import webrepl
#webrepl.start()
