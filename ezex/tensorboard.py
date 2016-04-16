import subprocess
import os
import time
import signal
import webbrowser
import random
import thread
from folder import Folder

def get_pid(port):
  for lsof in ["lsof","/usr/sbin/lsof"]:
    try:        
      pid = int(subprocess.check_output([lsof,"-t","-i:"+str(port)]))
      break
    except:
      pid = -1
  return pid


def tbfolder(experiments):
  ''' create temporary folder with a subset of experiment folders and tensorboard event files files for tensorboard '''
  
  tbf = Folder(folders=None, create=True) # temporary folder
  for f in experiments:
    tbf[f.name()].link(f.tb.filepaths())
  return tbf.path()


class Tensorboard:
  def __init__(self,logdir,host="127.0.0.1", port=None,force=True,stdout=False):
    ''' start tensorboard process reliably '''
    
    while port is None:
      port = random.randint(6006,6999)
      port = port if get_pid(port) == -1 else None
      
    self.port = port
    self.host = host
    
    #tbpath=os.path.dirname(tensorflow.__file__)+'/tensorboard/tensorboard.py'
    
    # free port
    if force:
      pid = get_pid(port)
      if pid != -1:
        os.kill(pid,signal.SIGTERM)
        print("Tensorboard: Killed process " + str(pid) + " to free port " + str(port))
    
    # launch tensorboard
    '''
    if stdout:
       DEVNULL = sys.stdout
    else:
       DEVNULL = open(os.devnull, 'wb')
   '''
    
    def run(self=self):
      self.output = None
      
      try:
        self.proc = subprocess.Popen(['tensorboard',
                                       "--host=" + self.host + " ",
                                       "--port=" + str(self.port) + " ",
                                       "--logdir=" + logdir],
                                       preexec_fn=os.setsid,
                                       shell=False,
                                       stderr=subprocess.STDOUT)
        self.proc.communicate()            
      except subprocess.CalledProcessError as err:
        self.output = err.output
      except Exception as ex:
        self.output = str(ex)          

    thread.start_new_thread(run,())
                           
    # check if running     
    time.sleep(2)
    if self.output is not None:
      raise RuntimeError("Tensorboard failed on port "+self.port+"\n"+"Output:\n"+self.ouput.getvalue())
    else:
      pass
      #print("Tensorboard started on port "+str(port))
    
    
  def openbrowser(self):
    webbrowser.open_new_tab('http://localhost:'+str(self.port))
    
  def kill(self):
    ''' kill tensorboard process '''
    os.kill(- self.proc.pid,signal.SIGTERM)
    #print("Tensorboard stopped")   
    
