import serial

import time
time.sleep(1)
s=serial.Serial("/dev/ttyS1",115200)

print s.inWaiting()
print s.read(s.inWaiting())


