import requests
import sys
import json


servername="localhost:9090"

if len(sys.argv)>1:
  servername=sys.argv[1]

servername="http://"+servername


endpoint=servername+"/api"


print("Server endpoint --- %s " % endpoint)

print("Enter to continue...")
raw_input()

testdevID="test_777"
testlog = {"device_id":"%s"%testdevID,"hello":"world"}


'''

print("Inserting device %s" % testdevID)
payload={"action":"insertdevice","payload":'{"device_id":"%s"}' % testdevID}
r=requests.get(endpoint,params=payload)
print r.text

raw_input()

'''

for count in range(100):
	testlog["logID"]=count
	print("Inserting log... %s" % testlog)

	payload={"action":"insertlog","payload":json.dumps(testlog)}


	r=requests.get(endpoint,params=payload)
	print (r.text)

	print("")

print ("\ntest complete....")


import os
print("Give permission to rebuild/clean/clear the database")
os.system("python ../model.py rebuild")
