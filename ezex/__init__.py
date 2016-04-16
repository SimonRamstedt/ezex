
from folder import Folder
import os
import json
import shutil
home = os.path.dirname(__file__)

def cwrite(data):
  with open(home+'/config.json','w') as f:
    json.dump(data,f)

def cread():
  with open(home+'/config.json') as f:
    return json.load(f)

if not os.path.isfile(home+'/config.json'):
	shutil.copy(home+'/default/config.json', home+'/config.json')

if not os.path.isfile(home+'/dashboard.ipynb'):
	shutil.copy(home+'/default/dashboard.ipynb', home+'/dashboard.ipynb')

config = cread()
if not config.has_key('exfolder'):
  config['exfolder'] = home+'/experiments'
if not config.has_key('scheduler'):
  config['scheduler'] = 'lsf'
cwrite(config)

exfolder = Folder(config['exfolder'],create=False)

