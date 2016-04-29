import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore", module="matplotlib")

from IPython.display import display
from ipywidgets import widgets 
import signal
import matplotlib.pyplot as plt

import time
import thread
import tensorboard
import numpy as np
from tensorboard import Tensorboard
import experiment
import cStringIO
import os

import __init__ as ezex
from ezex import Folder



def load(pattern):
  import glob
  import numpy as np
  data = [np.load(f) for f in glob.glob(ezex.config['exfolder']+'/'+pattern)]
  return data


def hist(pattern,savename,size=(12,4),color = "#99c2d7",scale=1):
    f,ax = plt.subplots()
    f.set_size_inches(*size)
    #f.set_tight_layout(True)
    #T = 132

    #color = "#009cda"
    

    #E = [ezex.exp_folder[n] for n in N]
    #R = [e.test_r for e in E]
    #I = E[0].test_i
    data = load(pattern+'/ezex.npy')
    R = [d[:,1] for d in data]
    I = data[0][:,0]

    first = 1
    T = np.min([len(r) for r in R])
    
    r = [ri[first:T-1] for ri in R]
    r = np.vstack(r)
    #print r

    i = np.linspace(0,1,T-1-first)

    # TODO: remove HACK!
    r = (r+300)*scale - 300
    # h = np.max(r)
    # l = np.min(r)

    #r = (r - l) / (h-l) 
    #print r

    # max = np.max(r,axis=0)
    # med = np.mean(r,axis=0)
    # min = np.min(r,axis=0)
    max = np.percentile(r,75,axis=0)
    med = np.percentile(r,50,axis=0)
    min = np.percentile(r,25,axis=0)

    ax.plot(i,med,'k-')
    ax.fill_between(i, min, max,color=color)
    ax.get_yaxis().set_ticks([-300-30,-45+30])
    ax.get_yaxis().set_ticklabels(['',''])
    ax.get_xaxis().set_ticks([0,1])
    ax.get_xaxis().set_ticklabels(["0",str(int(np.round(I[T-1]/100000)*100000))])
    offs = 1.005 # -0.07

    K = -45 #0.7
    ax.axhline(K,color='k',ls='dashed')
    ax.text(offs,K,'optimal',rotation=0)

    L = -100 #0.7
    ax.axhline(L,color='k',ls='dashed')
    ax.text(offs,L,'balance',rotation=0)

    M = -220 #0.45
    ax.axhline(M,color='k',ls='dashed')
    ax.text(offs,M,'swingup',rotation=0)

    #p = os.path.expanduser('~/'+name+'.png')
    p = os.path.expanduser(savename)
    f.savefig(p, format='png',dpi=120)

def dashboard(max=8):
  style_hlink = '<style>.hlink{padding: 5px 10px 5px 10px;display:inline-block;}</style>'
  exps = ezex.exfolder

  here = Folder('.')
  
  def killtb():
    if 'tb' in here:
      try:
        here.tb.kill()
      except:
        pass

  killtb()
  
  class exp_view:
    def __init__(self,e):
      self.e = e
      #self.name = widgets.Button(description=e.name())
      bname = widgets.HTML(style_hlink+
        '<a class=hlink target="_blank"'+
        'href="http://localhost:'+str(ezex.config['ip']) +'/tree/'+e.name()+'"> '+
        e.name() + ' </a> ')

      #self.run_type = widgets.Button()
      self.run_status = widgets.Button()

      #space = widgets.Button(description='     ')

      killb = widgets.Button(description='kill')
      delb = widgets.Button(description='delete')
      killb.on_click(lambda _,e=e: experiment.kill(e.path()))

      def delf(_,self=self):
        self.delete()
        experiment.delete(self.e.path())
      delb.on_click(delf)


      tbb = widgets.Button(description='tensorboard')
      tbbb = widgets.HTML(style_hlink+'<a class=hlink target="_blank" href="http://localhost:'+ str(ezex.config['tb']) +'"> (open) </a> ')
      
      def ontb(_,self=self):
        #folder = tensorboard.tbfolder([self.e])
        folder = self.e.path()
        killtb()
        tb = Tensorboard(folder,port=ezex.config['tb'],stdout=True)
        here.tb = tb
        # tb.openbrowser()
      tbb.on_click(ontb)

      self.bar = widgets.HBox((bname,self.run_status,tbb,tbbb,killb,delb))
      self.plot = widgets.Image(format='png')
      self.view = widgets.VBox((self.bar,self.plot,widgets.HTML('<br><br>')))

      self.th_stop = False
      def loop_fig(self=self):
        while not self.th_stop:
          try:
            # update plot
            try:
              x = np.load(self.e.path()+'/ezex.npy')
            except:
              x = np.zeros([1,2])

            #f = plt.figure()
            #f = Figure()
            f,ax = plt.subplots()
            f.set_size_inches((15,2.5))
            f.set_tight_layout(True)
            ax.plot(x[:,0],x[:,1])
            #ax.plot(i,r)
            sio = cStringIO.StringIO()
            f.savefig(sio, format='png',dpi=60)

            self.plot.value = sio.getvalue()

            sio.close()
            plt.close(f)
          except:
            pass

      self.th = thread.start_new_thread(loop_fig,())

    def update(self):
      try:
        # update labels
        x = experiment.xread(self.e.path())
        rt = x['run_type']
        rs = x['run_status']
        self.run_status.description = rt + ": " + rs

        # # alive?
        # try:
        #   mtime = os.path.getmtime(self.e.path()+'/test_r.npy')
        # except OSError:
        #   mtime = time.time()
        
        # if time.time()-mtime > 10*60: # heartbeat 10 min
        #   self.run_status.description = 'dead'
        # else:
        #   self.run_status.description = x['run_status']


      except:
        pass


    def delete(self):
      self.th_stop = True
  

  main_view = widgets.VBox()
  #display(widgets.HTML('<a target="_blank" href="http://localhost:'+ str(ezex.config['tb']) +'">fjdk</a>'))
  display(main_view)
  
  def loop():
    views = {}
    while True:
      try:
        views2 = {}
        todisplay = []

        i = 0
        for e in reversed(exps[:]):
          if i == max: break
          i = i+1
          v = views[e.name()] if e.name() in views else exp_view(e)
          v.update()
          todisplay = todisplay + [v.view]
          views2[e.name()] = v

        main_view.children = todisplay
        views = views2
        time.sleep(0.5)
      except Exception as ex:
          pass

  th = thread.start_new_thread(loop,())
  