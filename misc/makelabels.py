import os
logo = 'Halfway Crooks'
logofonts = ['big', 'script', 'shadow', 'slant', 'smascii12', 'standard']
for font in logofonts:
	os.system('figlet -p -f '+font+' '+logo+' > /home/halfway/BrewMenu/ascii_art/'+logo.split()[0].lower()+'_'+font+'_art.txt')
lbls = ['Name', 'Type', 'ABV', 'Pour', 'Cost']
lblfonts = ['future', 'emboss', 'bubble', 'digital', 'mini', 'small', 'smscript', 'smslant']
for lbl in lbls:
	for font in lblfonts:
		os.system('figlet -f '+font+' '+lbl+' > /home/halfway/BrewMenu/ascii_art/'+lbl.lower()+'_'+font+'_art.txt')
	#for font in os.listdir('/usr/share/figlet/'):
	#	if '.flc' not in font:
	#		os.system('figlet -f '+font+' '+lbl+' > '+lbl+'_'+font[:-4]+'_art.txt')
	
