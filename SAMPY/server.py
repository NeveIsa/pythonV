import os
import cherrypy
import jinja2
import yaml
import json
from pprint import pprint


### GLOBAL VARS ###

_config = yaml.load(open("_config.yml").read())

print "\nCONFIG..."
pprint(_config)
print ""


### GLOBAL VARS ###




### HELPERS ###

def frontmatter(filename):
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
    yamlData=yaml.load(yaml_part)
    return other_part,yamlData
  else:
    f=open(filename)
    return f.read(),None

def gfm2html(gfmsource):
  import markdown
  from mdx_gfm import GithubFlavoredMarkdownExtension
  html = markdown.markdown(gfmsource,extensions=[GithubFlavoredMarkdownExtension()])
  return html


def api_query(query):

  if query['data']=="pictures":
    albums_dir=_config["pictures_gallery"]
    albums=os.listdir(albums_dir)
    gallery={}
    for album in albums:
      album_path=os.path.join(albums_dir,album)
      gallery[album]=map(lambda x: os.path.join(album_path,x),os.listdir(album_path))

    return gallery  

### HELPERS ###

def render(template_name,**kwargs):
  templateLoader = jinja2.FileSystemLoader('_templates')
  templateEnv = jinja2.Environment( loader=templateLoader )
  try:
    return templateEnv.get_template("%s.html" % template_name).render(**kwargs)
  except:
    return templateEnv.get_template("%s.html" % "_404").render()


def render_post(template_name):
  #templateLoader = jinja2.FileSystemLoader('_posts')
  #templateEnv = jinja2.Environment( loader=templateLoader )
  templateEnv = jinja2.Environment()
  try:
    md_part,yaml_part=frontmatter("_posts/%s.html" % template_name)
    return jinja2.Template(gfm2html(md_part)).render()
    #return templateEnv.get_template().render()
  except:
    templateLoader = jinja2.FileSystemLoader('_templates')
    templateEnv = jinja2.Environment( loader=templateLoader )
    return templateEnv.get_template("%s.html" % "_404").render()


class Sampy(object):
  @cherrypy.expose
  def index(self):
    return render("index",_config=_config)

  @cherrypy.expose
  def posts(self,page):
    return render_post(page)

  @cherrypy.expose
  def picturesGallery(self):
    return render("_picturesGallery",_config=_config)

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def test(self):
    return {"hello":"world","okay":"ko"}

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def api(self,query):
    try:
      query=json.loads(query)
      return api_query(query)

    except Exception as e:
      #print e
      return {"status":"fail","exception":str(e)}


  def default(self, attr='abc'):
    return "Page not Found!"
    default.exposed = True

if __name__ == "__main__":


  def error_page_404(status, message, traceback, version):
    return render("_404")

  conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'error_page.404': error_page_404
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }

    }

  cherrypy.config.update({'server.socket_host': '0.0.0.0'} ) 

  cherrypy.quickstart(Sampy(), '/', conf)
