# ezex
ezex (i.e. easy experiment) is a lightweigt python package for managing experiment runs. It keeps all experiments in a single folder on a possibly shared file system and provides routines for starting/aborting jobs on computing clusters with LSF or SLURM

### Usage
```
usage: ezex {dashboard,remote,run,set}

positional arguments:
  {dashboard,remote,run,set,execute}
    dashboard           open jupyter notebook dashboard
    remote              dashboard on a remote maching via ssh port forwards
    run                 run experiments (i.e. python scripts)
    set                 set global ezex variables (e.g. experiment folder)

```

### Installation
```
sudo pip install ezex
```
or
```
pip install ezex --user
```