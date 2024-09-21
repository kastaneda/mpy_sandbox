import myStepper, time

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
