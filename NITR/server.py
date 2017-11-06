import os

from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(directories=['includes'])

#print(Template("hello ${data}!").render(data="world"))

import cherrypy
import model
import json
from bson import json_util
import datetime


def authUser(username,password):
	with open("credentials.json") as f:
		cred=json.loads(f.read().strip())

	if username in cred:
		if password==cred[username]:
			return True

	return False



def changePass(username,password_current,password_new):
	with open("credentials.json") as f:
		cred=json.loads(f.read().strip())
	if username in cred:
		if cred[username]==password_current:
			cred[username]=password_new
			with open("credentials.json",'w') as g:
			  g.write(json.dumps(cred))
			return True
		else:
			return False
	else:
		return False

class Root(object):
	#@cherrypy.expose
	#def test(self):
	#	return Template(filename='templates/test.html',lookup=mylookup).render()

	@cherrypy.expose
	def index(self):
		#print "logged" in cherrypy.session
		if not "logged" in cherrypy.session:
			raise cherrypy.HTTPRedirect("/login",status=303)
		elif cherrypy.session["logged"]==False:
			raise cherrypy.HTTPRedirect("/login",status=303)
		else:
			return Template(filename='templates/index.html',lookup=mylookup).render()

	@cherrypy.expose
	def login(self,username="",password=""):
		if cherrypy.request.method=="GET":
			if "logged" in cherrypy.session and cherrypy.session["logged"]==True:
				raise cherrypy.HTTPRedirect("/index",status=303)
			else:
				return Template(filename='templates/login.html').render(message="Login")

		#statements below will only be executed in case of POST
		if authUser(username,password):
			cherrypy.session["logged"]=True
			cherrypy.session["username"]=username
			raise cherrypy.HTTPRedirect("/",status=303)

		else:
			return Template(filename='templates/login.html').render(message="Bad Credentials.. Login Again")


	@cherrypy.expose
	def logout(self):
		cherrypy.session["logged"]=False
		raise cherrypy.HTTPRedirect("/login",status=303)

	@cherrypy.expose
	def changepass(self,currentpassword="",newpassword="",confirmpassword=""):
		if cherrypy.request.method=="GET":
			return Template(filename="templates/changepass.html").render()



		if cherrypy.session["logged"] and "username" in cherrypy.session:
			if newpassword==confirmpassword:
				if changePass(cherrypy.session["username"],currentpassword,newpassword):
					raise cherrypy.HTTPRedirect("/logout",status=303)
				else:
					return "Failed"
		else:
			raise cherrypy.HTTPRedirect("/logout",status=303)

	@cherrypy.expose
	def settings(self):
		return Template(filename="templates/settings.html",lookup=mylookup).render()


class Rest(object):
	exposed=True
	def GET(self,action,payload):
		cherrypy.response.headers['Content-type'] = "application/json"
		payload=json.loads(payload)
		if action=="insertlog":
			try:
				if not "device_id" in payload:
					raise Exception("'device_id' not found in payload")
				model.insertLogs([payload])
				return json.dumps({"status":"success","device_id":payload["device_id"]})
			except Exception as e:
				return json.dumps({"status":"failed", "exception" : str(e)})
		elif action=="getlog":
			try:
				if "device_id" in payload:
					device_id=payload["device_id"]
				else:
					device_id=None

				if "latestN" in payload:
					latestN=int(payload["latestN"])
					timedate_start,timedate_end=0,0

				else:
					latestN=None

					year,month,day = map(int,payload["date"].split("-"))
					#return "-".join(map(str,[year,month,day]))
					hour_start,min_start = map(int,payload["time_start"].split(":"))
					hour_end,min_end = map(int,payload["time_end"].split(":"))
					#return "-".join(map(str,[hour_start,min_start,hour_end,min_end]))

					timedate_end=timedate_start=datetime.datetime(year,month,day)

					timedate_start+=datetime.timedelta(seconds=hour_start*3600+min_start*60)
					timedate_end+=datetime.timedelta(seconds=hour_end*3600+min_end)
					#import pickle
					#pickle.dump((timedate_start,timedate_end,device_id,latestN),open("p.pkl","w"))

				result=model.getLogs(timedate_start,timedate_end,device_id=device_id,latestN=latestN)
				return json.dumps(result,default=json_util.default)

			except Exception as e:
				return json.dumps({"status":"failed", "exception" : str(e)})

		elif action=="insertdevice":
                        device={"device_id":payload['device_id']}
			if model.insertDevice(device):
				return json.dumps({'status':'success'})
			else:
				return json.dumps({'status':"failed"})

			#return json.dumps(result,default=json_util.default)

		elif action=="deletedevice":
			if not 'device_id' in payload:
				return json.dumps({'status':'failed','error':'device_id not present in payload'})

			device_id=payload['device_id']
			result=model.deleteDevice(device_id)
			if result:
				return json.dumps({"status":"success"},default=json_util.default)
			else:
				return json.dumps({"status":"failed"})
		elif action=="getdevice":
			if "device_id" in payload:
				result=model.getDevices(payload['device_id'])
			else:
				result=model.getDevices()
			#print result
			if result:
				return json.dumps(result,default=json_util.default)
			else:
				return json.dumps([])

		else:
			return json.dumps({"status":"failed","error":"Invalid action: " + action})



if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        },
        '/api': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        }
    }


    root=Root()
    root.api=Rest()

    cherrypy.config.update({'server.socket_host': '0.0.0.0','server.socket_port': 9090})
    cherrypy.quickstart(root, '/', conf)
