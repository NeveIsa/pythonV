import requests
import sys


servername="localhost:8080"

if len(sys.argv)>1:
  servername=sys.argv[1]

severname="http://"+servername


url=servername+"/api"
payload={"action":"insert","payload":'{"device_id":"777"}'}
r=requests.get(servername)
