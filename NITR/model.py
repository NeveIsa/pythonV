import datetime

from pymongo import MongoClient
client = MongoClient()
dbname="nitr"


db = client[dbname]
DEVLOGS=db.deviceLogs
DEVLIST=db.deviceList

def insertLogs(logs):
  finallogs=[]

  for log in logs:
    device_id = log["device_id"]
    timedate = datetime.datetime.now()
    finallogs.append({'device_id':device_id,'timedate':timedate,'rawlog':log,'formattedtime':timedate.strftime("%d-%m-%Y %H-%M-%S")})

  DEVLOGS.insert_many(finallogs)


def getLogs(timedate_start,timedate_end,device_id=None,latestN=None):
  if latestN:
    if device_id:
      cursor=DEVLOGS.find({'device_id':device_id}).limit(latestN)
    else:
      cursor=DEVLOGS.find().limit(latestN)
  else:
    query={}
    timedate_filter={'$gte':timedate_start, "$lt":timedate_end}
    if not device_id:
      query['timedate']=timedate_filter
    else:
      query['$and']=[{'timedate':timedate_filter},{'device_id':device_id}]

    #print query
    cursor = DEVLOGS.find(query).sort("timedate")

  finaldata=list(cursor)
  return finaldata



def insertDevice(device):
  if not type(device)==dict and "device_id" in device:
    return False
  device['timedate']=datetime.datetime.now()
  device["formattedtime"]=device['timedate'].strftime("%d-%m-%Y %H-%M-%S")
  DEVLIST.insert_one(device)
  return True

def deleteDevice(device_id):
  result=DEVLIST.delete_one({'device_id':device_id})
  #print dir(result)
  if result.deleted_count==1:
    return True
  else:
    return False

def getDevices(device_id=""):
  if device_id=="":
    result=DEVLIST.find()
    #print "ok",list(result)
  else:
    result=DEVLIST.find({'device_id':device_id})

  result=list(result)
  return result

if __name__=="__main__":

  #insertLogs([{"device_id":"100"}])
  #import pprint,time
  #time.sleep(1)
  #pprint.pprint(getLogs(datetime.datetime.now()-datetime.timedelta(seconds=2),datetime.datetime.now()+datetime.timedelta(seconds=1)))
  #pprint.pprint(getLogs(0,0,latestN=10))

  def regenerate_db():
    client.drop_database(dbname)
    db = client.nitr
    db.info.insert_one({"info_critical":"new db created"})

  import sys
  if len(sys.argv)>1:
    if sys.argv[1]=="rebuild":
      print "Are you sure? Y/n ... All the current data in the database will be deleted"
      if raw_input()=="Y":
	print "Removing..."
        regenerate_db()
        print "Removed..."
      else:
        print "No operations performed on database..."
