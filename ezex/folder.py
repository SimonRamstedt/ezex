import numpy as np
import os
import os.path as p
import shutil
import cPickle as pickle
import tempfile as tmp
import fcntl
import json

def cprint(x):
  pass

import os
from contextlib import contextmanager
from tempfile   import NamedTemporaryFile

if not hasattr(os, 'replace'):
    os.replace = os.rename #NOTE: it won't work for existing files on Windows

@contextmanager
def FaultTolerantFile(name):
    dirpath, filename = os.path.split(name)
    # use the same dir for os.rename() to work
    with NamedTemporaryFile(dir=dirpath, prefix=filename, suffix='.tmp') as f:
        yield f
        f.flush()   # libc -> OS
        os.fsync(f) # OS -> disc (note: on OSX it is not enough)
        f.delete = False # don't delete tmp file if `replace()` fails
        f.close()
        os.replace(f.name, name)
        
        

class Folder(object):
  def __init__(self,folders=None,create=False,rm=False):
    self._create = create
    
    if folders is None:
      # create empty tmp folder
      self._path = tmp.mkdtemp()
        
    else:
      # folder is single path string
      self._path = p.abspath(folders)
      if create:
        if p.isdir(self._path):
          if rm:
            try:
              shutil.rmtree(self._path)
              os.makedirs(self._path)
              cprint(self._path+" recreated")
            except:
              cprint("Unable to remove "+self._path)
        else:
          os.makedirs(self._path)
      else:
        if not p.isdir(self._path):
          raise KeyError('No folder at ' + self._path)
  
  def name(self):
    head, tail = p.split(self._path)
    return tail
    
  def path(self):
    return self._path
    
  def filenames(self):
    f = os.listdir(self._path)
    f.sort()
    return f
    
  def filepaths(self):
    r = []
    for f in self.filenames():
      r.append(p.join(self._path,f))
    return r
    
  def link(self,files):
    for f in files:
      head,tail = p.split(f)
      os.symlink(f,p.join(self._path,tail))
    
  def delete(self):
    shutil.rmtree(self._path,ignore_errors=True)    
    
    
  def copy(self,other):
    for f in other.filepaths():
      head,tail = p.split(f)
      if tail[0] != '.':
        dst = p.join(self.path(),tail)
        if p.islink(f):
          linkto = p.abspath(f+'/.')
          print(linkto)
          os.symlink(linkto, dst)
        elif p.isdir(f):
          Folder.copy(self[tail],other[tail])
        else:
          shutil.copy(f,dst)
          
  def __getattr__(self,key):
    ''' override dot operator e.g: obj.bla '''
    if key[0] == '_':
      return object.__getattribute__(self,key)

    npy = p.join(self._path,key+'.npy') 
    if p.isfile(npy):
      arr = np.load(npy)
      return arr
      
    pic = p.join(self._path,key+'.p')
    if p.isfile(pic):
      f = open( pic, "rb" )
      #fcntl.flock(f,fcntl.LOCK_SH)
      r = pickle.load( f )
      #fcntl.flock(f,fcntl.LOCK_UN)
      f.close()
      return r
    
    directory = p.join(self._path,key)
    if p.isdir(directory):
      return Folder(directory,self._create) 
    
    if self._create:
      return Folder(p.join(self._path,key),True)
      
    raise KeyError(str(key))
    #return None

  
  def __contains__(self,key):
    ''' override "in" operator e.g.: 'filex' in folder '''
    # TODO: abstract from supported file types
    fil = p.join(self._path,key)  
    npy = p.join(self._path,key+'.npy') 
    pic = p.join(self._path,key+'.p')
    
    return p.isfile(npy) or p.isfile(pic) or p.isdir(fil)
    
    
  def __setattr__(self,key,value):
    ''' override dot operator e.g.: obj.bla = something '''
    # TODO: use non-blocking and "atomic" write
  
    if key[0] == '_':
      object.__setattr__(self,key,value)
    elif type(value) is np.ndarray:
      with FaultTolerantFile(p.join(self._path,key+'.npy')) as f:
        np.save(f,value)
    elif type(value) is Folder:
      # TODO: copy option
      # move all files and remove dir
      fol = Folder(p.join(self._path,key),create=value._create)
      f = os.listdir(value._path)
      for el in f:
        shutil.move(p.join(value._path,el),p.join(fol._path,el))
      os.rmdir(value._path)
    else:
      with FaultTolerantFile(p.join(self._path,key+'.p')) as f:
        pickle.dump(value,f)
      
  
  def __getitem__(self, key):
    ''' override brackets operator e.g.: obj[3] or obj['bla'] '''
    if type(key) is str:
      return Folder.__getattr__(self,key)
    else:
      f = self.filenames()
      files = f[key]
      if type(files) is list:
        res = []
        for f in files:
          name,ext = p.splitext(f)
          res.append(Folder.__getattr__(self,name))
        return res
      else:
        name,ext = p.splitext(files)
        return Folder.__getattr__(self,name)
      
  # override brackets operator e.g.: obj['bla'] = Folder()
  def __setitem__(self, key, value):
    return self.__setattr__(key,value)
    
  # usage: len(obj) -> number of files in folder
  def __len__(self):
    return len(os.listdir(self._path))
    
      
  
if __name__ == "__main__":
  print("test")