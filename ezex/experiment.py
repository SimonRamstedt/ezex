from folder import Folder
import time
from datetime import datetime
import thread
import subprocess
import shutil
import json
import os
import __init__ as ezex
import util

def xwrite(path,data):
  with open(path+'/ezex.json','w+') as f:
    json.dump(data,f)

def xread(path):
  with open(path+'/ezex.json') as f:
    return json.load(f)


def create(run_folder,tag=''):
  ''' create unique experiment folder '''
  
  rf = Folder(run_folder)
  
  #basename = 'e'+str(int(time.time()))+'_'+rf.name()
  dstr = datetime.now().strftime('%Y%m%d_%H%M_%S')
  basename =  dstr+'_'+rf.name()+'_'+tag
  name = basename
  i = 1
  while name in ezex.exfolder:
    name = basename + '_' + str(i)
    i = i+1
    if i > 100:
      raise RuntimeError('Could not create unique experiment folder')
      
  # ezex.exp_folder[name] = Folder(create=True)
  # exp = ezex.exp_folder[name]
  # exp.copy(rf)
  path = ezex.config['exfolder']+'/'+name
  os.mkdir(path)
  util.copy(run_folder,path,symlinks=True,ignore='.*')
  return path


def submit(path):
  x = xread(path)
  if ezex.config['scheduler']=='lsf':
    nvd = 'select[nvd]' if x['nvd'] else ''
    cmd = ('bsub -q deflt_centos -M 20000 -W 24:00 -n 4 -R "'+nvd+'" -x '+
      '-oo '+path+'/out '+
      '\''+ 'ezex execute ' + path +'\'')

    print(cmd)
    out = subprocess.check_output(cmd,shell=True)
    
    import re
    match = re.match('Job <(\d*)>',out)
    if match:
      jid = match.group(1)
    else:
      raise RuntimeError()

  elif ezex.config['scheduler']=='slurm':
    nvd = '#SBATCH -C nvd \n' if x['nvd'] else ''
    print(path)
    jscr = ("#!/bin/bash" + '\n' +
            "#SBATCH -o " + path + '/out' + '\n' +
            "#SBATCH --mem-per-cpu=" + "5000" + '\n' +
            "#SBATCH -n 4" + '\n' +
            "#SBATCH -t 24:00:00" + "\n" +
            nvd +
            "ezex execute " + path)

    with open(path+"/slurmjob","w") as f:
      f.write(jscr)

    cmd = "sbatch " + path + "/slurmjob"

    out = subprocess.check_output(cmd,shell=True)
    print("SUBMIT: \n" + out)

    import re
    #match = re.match('Submitted batch job (\d*)',out)
    match = re.search('Submitted batch job (\d*)',out)
    if match:
      jid = match.group(1)
    else:
      raise RuntimeError()

  else:
    raise RuntimeError('No scheduling system (e.g. SLURM) present')

  x['job_id'] = jid
  xwrite(path,x)


def execute(path,deltime=3*60):
  x = xread(path)
  t_start = time.time()
  try:
    cmd = x['cmd']
    x['run_status'] = 'running'
    xwrite(path,x)
    print(cmd)
    #os.system(cmd)
    subprocess.check_call(cmd,shell=True)
    x['run_status'] = 'finished'
  except:
    x['run_status'] = 'aborted'
    print("aborted")
  finally:
    elapsed = time.time() - t_start
    x['end_time'] = time.time()
    xwrite(path,x)
    print('elapsed seconds: ' + str(elapsed))
    if elapsed <= deltime:
      shutil.rmtree(path,ignore_errors=False)




def kill(path):
  try:
    x = xread(path)
    if ezex.config['scheduler']=='lsf':
      jid = x['job_id']
      cmd = 'bkill '+str(jid)
      out = subprocess.check_output(cmd,shell=True)
    elif ezex.config['scheduler']=='slurm':
      jid = x['job_id']
      cmd = 'scancel '+str(jid)
      out = subprocess.check_output(cmd,shell=True)
    else:
      return False
  except Exception as ex:
    return False


def delete(path):
  # TODO: simplify!
  kill(path)
  def deletet(path=path):
    t = time.time()
    suc = False
    exc = None
    def errorRemoveReadonly(func, path, exc):
      import errno
      import stat
      excvalue = exc[1]
      if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        # change the file to be readable,writable,executable: 0777
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  
        # retry
        func(path)
      else:
        exc = "Deletion of "+path+" not possible"
        
    while (time.time()-t < 2):
      try:
        shutil.rmtree(path,ignore_errors=False,onerror=errorRemoveReadonly) 
        suc = not os.path.isdir(path)
        if suc: break
      except Exception as ex:
        exc = ex

      time.sleep(0.2)

    if not suc:
      print(exc)

  thread.start_new_thread(deletet,())