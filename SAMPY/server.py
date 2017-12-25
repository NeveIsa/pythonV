import os,sys
import cherrypy
import jinja2
import requests
import yaml
import json
import datetime
from pprint import pprint

import uuid
import glob
import textile

import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension


import io #for utf-8 file read/write

### GLOBAL VARS ###

__STATIC_DIR = './static'

_config = yaml.load(open("_config.yml").read())

print "\nCONFIG..."
pprint(_config)
print ""


### GLOBAL VARS ###




### HELPERS ###


# Configure YAML for Ordered YAML LOADING and Dumping
import collections
_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())
def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))
yaml.add_representer(collections.OrderedDict, dict_representer)
yaml.add_constructor(_mapping_tag, dict_constructor)



def frontmatter(filename):
  """
  Returns other_part,yamlData after parsing from document frontmatter

  """
  yaml_part=""
  f=open(filename)
  line=f.readline()
  if line.replace("\n","").strip()=="---":
    for x in range(100):
      line=f.readline()
      if line.replace("\n","").strip()=="---":
        break
      yaml_part+=line
    other_part=f.read()
    f.close()
    yamlData=yaml.safe_load(yaml_part)

    #print yaml.dump(yamlData,default_flow_style=False)

    #insert Document UUID if not present
    if not 'DOCUUID' in yamlData:
      DOCUUID=str(uuid.uuid4())
      yamlData['DOCUUID']=DOCUUID

      #Update the doc with the new yaml containing DOCUUID

      #updated_yaml="---\n"+yaml.dump(yamlData,default_flow_style=False)+"---\n" 

      yaml_part_lines=yaml_part.split("\n")
      #append DOCUUID
      yaml_part_lines.append("DOCUUID: %s"%DOCUUID) 

      updated_yaml="---\n"+ "\n".join(yaml_part_lines) + "\n---\n"

      updated_doc= updated_yaml + other_part

      with open(filename,'w') as g:
        g.write(updated_doc)

      #(!!!CAUTION)Stack call -- this time frontmatter contains DOCUIID
      try:
        return frontmatter(filename)
      # If something has gone wrong with the DOCUIID insertion in the previous steps,
      # we need to restore the file back as otherwise we will lose the document
      except Exception as e:
        restored_doc=yaml_part+other_part
        with open(filename+".restored",'w') as g:
          g.write(restored_doc)

        with open(filename,'w') as g:
          g.write(restored_doc)

        print("----> Exception in frontmatter:",e)



    return other_part,yamlData
  else:
    f=open(filename)
    return f.read(),None

def gfm2html(gfmsource):
  html = markdown.markdown(gfmsource,extensions=[GithubFlavoredMarkdownExtension()])
  return html


def api_query(query):

  if query['data']=="pictures":
    albums_dir="."+_config["pictures_gallery"]
    albums=os.listdir(albums_dir)
    gallery={}
    for album in albums:
      album_path=os.path.join(albums_dir,album)

      albuminfo_path=os.path.join(album_path,"info.txt")
      if os.path.exists(albuminfo_path):
        info=open(albuminfo_path).read()
      else:
        info="No description present for this album..."

      #filter the info.txt file below
      gallery[album]={"images":map(lambda x: os.path.join(album_path,x),filter(lambda x:not x.endswith(".txt"),os.listdir(album_path))),"info":info}
    return gallery  

  elif query['data']=="quote":
    quote_src="https://quotes.rest/qod"
    quote_file=__STATIC_DIR+"/quotes.json"
    if os.path.exists(quote_file):
      with io.open(quote_file) as f:
        try:
          quote=json.loads(f.read())
          #CHECK IF QUOTE IS FROM TODAY -- server return UTC time
          if quote["contents"]["quotes"][0]["date"]==datetime.datetime.utcnow().strftime("%Y-%m-%d"):
            return quote
        except:
          print("Error parsing quotes.json")
          pass

    quote=requests.get(quote_src,headers={"Accept": "application/json"}).text

    with io.open(quote_file,'w') as g:
      g.write(quote)
    return json.loads(quote)

  elif query["data"]=="allposts":
    return ALL_POSTS_SUMMARY

  else:
    return {"status":"fail","reason":"Invalid data parameter in query json"}



def frontpost(posts_directories):
  '''
  Produces summary report of all posts from
  their front matter
  '''

  aggregate_summary={}

  for folder in posts_directories:
    print("frontpost ---> %s" % folder)
    files=[]
    folder_summary={}


    #Add files ending with .md,.markdown or .textile
    
    filetypes=map(lambda x:os.path.join(folder,x),["*.md","*.markdown","*.textile"])

    for filetype in filetypes:
      files.extend(glob.glob(filetype))
      #print filetype

    print("Found files in %s..." % folder)


    for file in files:
      print("  %s"%file)
      rest,yaml=frontmatter(file)

      # Add parent folder name to the file summary 
      if not yaml:
        yaml={}

      yaml["parent_folder"]=folder

      justDfilename=os.path.split(file)[-1]
      folder_summary[justDfilename]=yaml
      #print(yaml)

    folder_summary_file = os.path.join(folder,"folder_summary.json")
    #print("Generating {} for {}\n".format(folder_summary_file,folder))
    
    aggregate_summary[folder]=folder_summary 

  pprint(aggregate_summary)

  return aggregate_summary



def refreshPostSummary():
  return frontpost(map(lambda x:os.path.join(POSTS_FOLDER,x),filter(lambda x:os.path.isdir(os.path.join(POSTS_FOLDER,x)),os.listdir(POSTS_FOLDER))))

### HELPERS ###

def render(template_name,**kwargs):
  templateLoader = jinja2.FileSystemLoader('_templates')
  templateEnv = jinja2.Environment( loader=templateLoader )
  try:
    return templateEnv.get_template("%s.html" % template_name).render(**kwargs)
  except Exception as e:
    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    return templateEnv.get_template("%s.html" % "_404").render()


def render_post(post_folder,post_name):
  #templateLoader = jinja2.FileSystemLoader('_posts')
  #templateEnv = jinja2.Environment( loader=templateLoader )
  templateEnv = jinja2.Environment()
  try:

    post_files=glob.glob("_posts/%s/%s.*" % (post_folder,post_name))
    if len(post_files)>0:
      post_files.sort()
      post_file=post_files[0]
      if post_file.endswith(".md"):
        md_part,yaml_data=frontmatter(post_file)
        html_post=gfm2html(md_part)
      elif post_file.endswith(".textile"):
        textile_part,yaml_data=frontmatter(post_file)
        html_post=textile.textile(textile_part)

        
    _config["local"]=yaml_data
    return render("post",_config=_config,_POSTContent=html_post)
    #return jinja2.Template(gfm2html(md_part)).render()
    #return templateEnv.get_template().render()
  except Exception as e:
    templateLoader = jinja2.FileSystemLoader('_templates')
    templateEnv = jinja2.Environment( loader=templateLoader )
    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    return templateEnv.get_template("%s.html" % "_404").render()


class Sampy(object):

  @cherrypy.expose
  def index(self):
    return render("index",_config=_config)

  @cherrypy.expose
  def posts(self,folder="",post_name=""):
  	if not folder and not post_name:
  		return render("allposts",_config=_config)
  	elif not post_name:
  		_config["highlightFolder"]=folder
  		return render("allposts",_config=_config)
  	else:
  		return render_post(folder,post_name)


  @cherrypy.expose
  def picturesGallery(self):
    return render("_picturesGallery",_config=_config)

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def test(self,name):
    return name
    return {"hello":"world","okay":"ko"}

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def api(self,query):
    try:
      query=json.loads(query)
      #print json.dumps(query)
      return api_query(query)

    except Exception as e:
      #print e
      return {"status":"fail","exception":str(e)}


  def refresh(self):
    global ALL_POSTS_SUMMARY
    ALL_POSTS_SUMMARY=refreshPostSummary()
    
  def default(self, attr='abc'):
    return "Page not Found!"
    default.exposed = True

if __name__ == "__main__":

  POSTS_FOLDER="_posts"
  ALL_POSTS_SUMMARY=refreshPostSummary()

  def error_page_404(status, message, traceback, version):
    return render("_404")

  conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'error_page.404': error_page_404,
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': __STATIC_DIR
        }

    }

  cherrypy.config.update({'server.socket_host': '127.0.0.1', 'server.socket_port': 7070} ) 

  cherrypy.config.update({'log.screen': True,
                            'log.access_file': 'logs/access.log',
                            'log.error_file': 'logs/error.log'})

  cherrypy.quickstart(Sampy(), '/', conf)
