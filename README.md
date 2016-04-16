# ezex
ezex (i.e. easy experiment) is a lightweigt python package for managing experiment runs. It keeps all experiments in a single folder and provides routines for starting/aborting jobs on computing clusters with *lsf* or *slurm* schedulers.

### Usage
#### ezex dashboard
![dashboard](doc/db.png)
`ezex dashboard` opens a [jupyter notebook](http://jupyter.org/) which can be used to visualize the experiments (type *Shift+Enter* to execute a cell). If [TensorFlow](https://www.tensorflow.org/) is installed, experiments can also be visualized in tensorboard by clicking on *tensorboard* and then on *open*. Currently only one experiment at a time can be visualized in tensorboard.
To show a graph for each experiment the dashboard looks for a serialized *n* by *2* numpy array named `ezex.npy` in each experiment folder, generated for example by `np.save('ezex.npy', X)`.

#### ezex remote
`ezex remote <host> <user>` forwards an ezex dashboard from a remote machine. Both machines require ezex and password-free ssh has to be set up.

#### ezex run
`ezex run <path> <tag>` runs script at `<path>` by copying the folder containing it to a unique experiment folder and then submitting a job to a scheduler (e.g. slurm) to execute the copy. The `-l` option executes the copy on the local machine without submitting a job.

### Installation
```
sudo pip install ezex
```
or
```
pip install ezex --user
```
In the second case it might be nessessary to add `export PATH=$PATH:$HOME/.local/bin` to `~/.profile`. The experiment folder can be changed e.g. via `ezex set -exfolder <path>`.