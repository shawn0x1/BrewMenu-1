import os
from time import sleep

fontdir = '/usr/share/figlet'
for item in os.listdir(fontdir):
	type = str(item)[-2:]
	if type == 'lf': #'tlf' or type == 'flf'
		font = item[:-4]
		print(f'Font: {font}\n')
		os.system('figlet -t -f '+font+' '+font)
		print('\n'+'='*20)
		sleep(0.5)
