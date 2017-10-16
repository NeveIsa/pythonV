import socket,serial
import sys,subprocess


ttyports=subprocess.check_output("ls /dev/ttyUSB*",shell=1)
ttyports=ttyports.split('\n')[:-1]
ttyportTX=ttyports[0]


print "Connect RX to port:",ttyports[1],"and hit RETURN"
raw_input()

ser=serial.Serial(ttyportTX,115200)

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(("10.208.20.42",9090))


while 1:
  rx=s.recv(200)
  print rx,
  ser.write(rx)

