import gc
print('Free memory:', gc.mem_free())

#import link
#import cfg
#link.up(cfg.wifi)
#print('Free memory:', gc.mem_free())

#gc.collect()
#print('Free memory:', gc.mem_free())

import drv
drv.init()
print('Free memory:', gc.mem_free())
