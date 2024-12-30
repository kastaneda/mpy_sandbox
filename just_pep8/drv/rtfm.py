def m1_invert():
    mask = list(drv.m1._bitmask)
    mask.reverse()
    drv.m1._bitmask = tuple(mask)
