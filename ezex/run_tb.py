from tensorboard import Tensorboard
import __init__ as ex
from __init__ import Folder

if __name__ == '__main__':
  exps = ex.exp_folder[:]
  folder = ex.tbfolder(exps[-1:])
  port=6005
  tb = Tensorboard(folder,port=port)
  tb.openbrowser()