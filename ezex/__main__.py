import os
import argparse
import subprocess
import ezex
import experiment
import util

parser = argparse.ArgumentParser(description='ezex is a lightweigt destributed experimentation framework')
subparsers = parser.add_subparsers(dest='command')

p_vis = subparsers.add_parser('dashboard', help='open jupyter notebook dashboard')
p_vis.add_argument('-remote',action='store_true')
p_vis.add_argument('-db',type=int,default=6007)
p_vis.add_argument('-ip',type=int,default=6008)
p_vis.add_argument('-tb',type=int,default=6009)

p_rem = subparsers.add_parser('remote', help='dashboard on a remote maching via ssh port forwards')
p_rem.add_argument('host')
p_rem.add_argument('user')
#p_rem.add_argument('--password',default=None)
p_rem.add_argument('-db',default='6007')
p_rem.add_argument('-ip',default='6008')
p_rem.add_argument('-tb',default='6009')

p_run = subparsers.add_parser('run', help='run experiments (i.e. python scripts)')
p_run.add_argument('path',help='path to python script')
p_run.add_argument('tag',default='')
p_run.add_argument('-l',action='store_true',help='run on this machine')
p_run.add_argument('-nvd',action='store_true',help='run on Nvidia-Node')
p_run.add_argument('-preload',default=None,help='LD_PRELOAD=<PRELOAD> (path relative to script folder)')
p_run.add_argument('-prerun',default=None,help='run this command before the main script')
p_run.add_argument('-python2',action='store_true',help='use "python2" instead of "python" to run the script')

p_set = subparsers.add_parser('set', help='set user ezex variables (stored in ~/.ezex/)')
p_set.add_argument('-exfolder',help='path to experiment folder')
p_set.add_argument('-scheduler',help='lsf or slurm')

p_exe = subparsers.add_parser('execute', help='locally run python script (internal)')
p_exe.add_argument('path',help='path to experiment')

args = parser.parse_args()


if args.command == 'set':
	c = ezex.cread()
	if args.exfolder:
		if not os.path.isdir(args.exfolder):
			os.mkdir(args.exfolder)
		c['exfolder'] = args.exfolder
	if args.scheduler:
		c['scheduler'] = args.scheduler
	ezex.cwrite(c)


if args.command == 'dashboard':
	print('Experiment root folder at: ' + ezex.config['exfolder'])
	print('containing ' + str(len(ezex.exfolder[:])) + ' experiments')
	print('')

	util.free_port(args.db)
	util.free_port(args.ip)
	util.free_port(args.tb)

	c = ezex.cread()
	c['db'] = args.db
	c['ip'] = args.ip
	c['tb'] = args.tb
	ezex.cwrite(c)

	proc = subprocess.Popen(('jupyter notebook --no-browser --port='+str(args.ip) +' '+c['exfolder']).split(' '))

	if not os.path.exists(ezex.home+'/home'):
		cwd = os.getcwd()
		os.chdir(ezex.home)
		os.symlink(os.path.expanduser('~'),'home')
		os.chdir(cwd)

	f = ezex.home+'/dashboard.ipynb'
	os.system('jupyter notebook --port='+str(args.db) +' '+f)
	
if args.command == 'remote':
	import os
	import argparse
	import ezex
	import thread
	import webbrowser

	webbrowser.open_new_tab('http://localhost:'+str(args.db)+'/tree/dashboard.ipynb')

	util.free_port(args.db)
	util.free_port(args.ip)
	util.free_port(args.tb)
	
	cmd = ('ezex dashboard -remote' +
					 ' -db ' + str(args.db) +
					 ' -ip ' + str(args.ip) +
					 ' -tb ' + str(args.tb) )

	os.system("ssh -c arcfour "+args.user+"@"+args.host+
						" -L "+args.db+":localhost:"+args.db+
						" -L "+args.ip+":localhost:"+args.ip+
						" -L "+args.tb+":localhost:"+args.tb+
						" '"+cmd+"'")


if args.command == 'run':
	run_folder = os.path.dirname(args.path)
	run_script = os.path.basename(args.path)
	path = experiment.create(run_folder,args.tag)

	preload = '' if not args.preload else 'LD_PRELOAD='+ args.preload
	prerun = '' if not args.prerun else args.prerun+';'
	python = 'python2' if args.python2 else 'python'
	cmd = '/bin/bash -c "'+ prerun +'cd '+ path +';'+ preload +' '+python+' '+run_script+'"'

	experiment.xwrite(path,{'run_type':'local' if args.l else 'job',
													'run_status':'pending',
													'nvd':args.nvd,
													'cmd':cmd})
	if args.l:
	  print('run local')
	  experiment.execute(path)
	else:
	  print('submit job')
	  experiment.submit(path)


if args.command == 'execute':
	experiment.execute(args.path)