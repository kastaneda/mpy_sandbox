def test():
    avg = 0
    for x in range(1000):
        t1=sensor1.readTemp()
        t2=sensor2.readTemp()
        d=(t2-t1)/t1
        avg+=d
    return avg
    
sensor1.ntc.nominalR = 10000
sensor2.ntc.nominalR = 10060

avg1=0
avg2=0
for x in range(1000):
    avg1+=sensor1.readResistance()
    avg2+=sensor1.readResistance()
print(avg1 / 1000)
print(avg2 / 1000)
