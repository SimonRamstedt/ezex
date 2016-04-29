
from folder import Folder
import os
import json
import shutil
src = os.path.dirname(__file__)
home = os.path.expanduser('~/.ezex')

if not os.path.isdir(home):
	os.mkdir(home)

def cwrite(data):
  with open(home+'/config.json','w+') as f:
    json.dump(data,f)

def cread():
  with open(home+'/config.json') as f:
    return json.load(f)

if not os.path.isfile(home+'/config.json'):
	shutil.copy(src+'/default/config.json', home+'/config.json')

if not os.path.isfile(home+'/dashboard.ipynb'):
	shutil.copy(src+'/default/dashboard.ipynb', home+'/dashboard.ipynb')

config = cread()
if not config.has_key('exfolder'):
  config['exfolder'] = home+'/experiments'
  
if not os.path.isdir(config['exfolder']):
	os.mkdir(config['exfolder'])

if not config.has_key('scheduler'):
  config['scheduler'] = 'slurm'
cwrite(config)

exfolder = Folder(config['exfolder'],create=False)



