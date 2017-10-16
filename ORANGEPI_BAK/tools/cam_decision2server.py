import serial
import os,subprocess,sys,time

try:
  ser=serial.Serial("/dev/ttyUSB0",115200)
  serial_status=True
  print "Mote Detected..."
except:
  serial_status=False
  print "Mote not detected.. will try UDP over LAN directly"


packet_id=0


intruderFile="log/intruder.txt"

while 1:
  if not os.path.exists(intruderFile):
    print "%s file not found..." % intruderFile
    time.sleep(1)
  else:
    print "FOUND INTRUDER FILE",intruderFile
    print "FIRST INTRUSION...waiting for 20s"
    time.sleep(20)
    break
  #sys.exit(1)


def total_intrusion_lines():
  f=open(intruderFile)
  data=f.read()
  f.close()
  data=data.split("\r\n")[:-1]
  data_line_length = map(lambda v: len(v),data)
  from collections import Counter
  no_of_intruders = Counter(data_line_length).values()[0] 
  # get no of zeroes, index 0 contains it as Counter sorts the keys in Counter(data_line_lenght).keys() 
  return no_of_intruders



def handle_new_intruder():
  f=open(intruderFile)
  data=f.read()
  f.close()
  data=data.split("\r\n")[:-1]
  while 1:
    if data[-1]=="":
      data=data[:-1]
    else:
      break
  #print data
  data.reverse()
  #print ""
  #print data
  try:
    pos_of_blank_line = data.index("")
  except:
    pos_of_blank_line=len(data)
    print "FIRST DETECTION...."
    #time.sleep(10) #first detection has no new line, so wait for some time or we  get multiple detections

  data=data[:pos_of_blank_line]
  #print ""
  #print data

  try:
    data=map(lambda x:x.split(",")[-1],data)
  except:
    return

  no_animal=data.count("0")
  no_human=data.count("1")
  global packet_id
  packet_id+=1
  #print packet_id
  print "H : A ::",no_human,":",no_animal
  if no_human < no_animal:
    _intruder="Animal"
  else:
    _intruder="Human"
  udp_packet = "%s : %s detected!!!\n" % (str(packet_id),_intruder)
  print udp_packet
  
  if serial_status==False:
    print "UDP over LAN"
    import socket
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("10.208.20.50",5678))
    s.sendall(udp_packet)

  else:
    print "UDP over MOTE"
    global ser
    ser.write(udp_packet)
    print ""
    time.sleep(1)
    print ser.read(ser.inWaiting())

last_intr_lines=total_intrusion_lines()

#x=handle_new_intruder()


#exit()


while 1:
  intr_lines=total_intrusion_lines()
  if last_intr_lines==intr_lines:
    time.sleep(3) # no new intrusions
  else:
    handle_new_intruder()
    time.sleep(10)
    last_intr_lines=total_intrusion_lines()


