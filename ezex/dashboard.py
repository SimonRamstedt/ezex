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
from tensorboard import Tensorboard
import experiment
import cStringIO
import os

import __init__ as ezex
from ezex import Folder

style_hlink = '<style>.hlink{padding: 5px 10px 5px 10px;display:inline-block;}</style>'

exps = ezex.exfolder

def dashboard(max=8):
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

      self.run_type = widgets.Button()
      self.run_status = widgets.Button()

      space = widgets.Button(description='     ')

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
        folder = self.e.path()+'/tb'
        killtb()
        tb = Tensorboard(folder,port=ezex.config['tb'],stdout=True)
        here.tb = tb
        # tb.openbrowser()
      tbb.on_click(ontb)

      self.bar = widgets.HBox((bname,self.run_type,self.run_status,space,tbb,tbbb,space,killb,delb))
      self.plot = widgets.Image(format='png')
      self.view = widgets.VBox((self.bar,self.plot,widgets.HTML('<br><br>')))

      self.th_stop = False
      def loop_fig(self=self):
        while not self.th_stop:
          try:
            # update plot
            try:
              r = self.e.test_r
              i = self.e.test_i
            except:
              r = 0
              i = 0
            #f = plt.figure()
            #f = Figure()
            f,ax = plt.subplots()
            f.set_size_inches((15,2.5))
            f.set_tight_layout(True)
            ax.plot(i,r)
            sio = cStringIO.StringIO()
            f.savefig(sio, format='png',dpi=60)

            self.plot.value = sio.getvalue()

            sio.close()
            plt.close(f)
          except:
            pass #print ex

      self.th = thread.start_new_thread(loop_fig,())

    def update(self):
      try:
        # update labels
        x = experiment.xread(self.e.path())
        self.run_type.description = x['run_type']
        
        # alive?
        try:
          mtime = os.path.getmtime(self.e.path()+'/test_r.npy')
        except OSError:
          mtime = time.time()
        
        if time.time()-mtime > 10*60: # heartbeat 10 min
          self.run_status.description = 'dead'
        else:
          self.run_status.description = x['run_status']
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
          #print ex

  th = thread.start_new_thread(loop,())
  