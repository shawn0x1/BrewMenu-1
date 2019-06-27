import os

cmd = 'avconv -re -i movies/{0} -vcodec copy -f avi -an udp://239.0.1.23:1234'
for file in os.listdir('/home/master/movies'):
	os.system(cmd.format(file))

