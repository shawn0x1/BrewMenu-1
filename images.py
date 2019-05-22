# ASCII image collection for BrewMenu
# import curses
from curses import COLOR_BLACK, COLOR_GREEN
import os
import random
from values import *


def terminal_width():
	return int(os.popen('stty size', 'r').read().split()[1])

def terminal_height():
	return int(os.popen('stty size', 'r').read().split()[0])

def longest_str(str_list):
	max_len = 0
	for item in enumerate(str_list):
		# if len(str(item)) > max_len:
		# 	max_len = len(str(item))
		for s in item:
			if len(str(s)) > max_len:
				max_len = len(str(s))
	# os.system('echo "max_len = '+str(max_len)+'" >> menu_debug.log')
	return max_len #, num_items

last_box_x = 5
def draw_error_window(window, x=5):
	global last_box_x
	# box = window.derwin(10, 10, 5, 5)
	box_height = 10
	box_width = 10
	y = 5
	# x = last_box_x + 1
	# last_box_x += box_width
	box = window.subwin(box_height, box_width, y, x)
	box.box()
	# box.addstr(1, 1, "ERR")
	# box.addstr(2, 1, "ERR")
	for i in range(1, box_height-1):
		box.addstr(i, 1, "ERR")


art_dir = os.getcwd() + '/ascii_art'
file_dict = {}

# Must `sudo apt-get install toilet figlet` on the host system
def get_art(font, text, key, usetoilet=False):
	art = []
	if not os.path.isdir(art_dir):
		os.mkdir(art_dir)
	#key = key.replace(' ', '_')
	key = key.strip().lower()
	out_file = art_dir + '/' + key + '_' + font + '_art.txt'
	file_dict.update({key : out_file})
	if not os.path.isfile(out_file):
		if usetoilet:
			cmd = 'toilet "' + text + '" -f ' + font + ' -WSkt > ' + out_file
		else:
			cmd = 'figlet -f '+font+' '+text+' > '+out_file
		os.system(cmd)
	with open(out_file) as f:
		art = f.readlines()
	return art

def load_from_file(path):
	art = None
	try:
		with open(path, 'r') as f:
			art = f.read().split('\n')
	except:
		pass
	return art

def make_with_asciimatics(text, name, fontsize='big'):
	filename = '{}.img'.format(name)
	if not os.path.isfile(filename):
		from asciimatics.renderers import FigletText
		os.system('echo "{}" >> {}'.format(FigletText(text,font=fontsize), filename))
	return load_from_file(filename)

logo = {
	'text': get_art(logo_font, logo_title, 'logo') if not (IMGFROMFILE and os.path.isfile(LOGOFILE)) else load_from_file(LOGOFILE),
	# 'label': logo_title,
	'key': 'logo',
	'font': logo_font,
	'col_offset': terminal_width() - 1, #10, #logo_offset,
	'width': longest_str(get_art(logo_font, logo_title, 'logo')),
	'row_offset': 0,
	'color': logo_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
	}


lbls_row_offset = int(terminal_height() / 4)
col_offset_base = 0
col_offset_step = 10


def label_col_offset(idx):
	return terminal_width() - (col_offset_base + (col_offset_step * idx)) # abs(idx - len(col_lbls))))


lbl0 = {
	'key': col_lbls[0],
	'font': lbls_font,
	'col_offset': label_col_offset(0),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[0], col_lbls[0]),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl1 = {
	'key': col_lbls[1],
	'font': lbls_font,
	'col_offset': label_col_offset(1),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[1], col_lbls[1]),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl2 = {
	'key': col_lbls[2],
	'font': lbls_font,
	'col_offset': label_col_offset(2),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[2], col_lbls[2]),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl3 = {
	'key': col_lbls[3],
	'font': lbls_font,
	'col_offset': label_col_offset(3),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[3], col_lbls[3]),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl4 = {
	'key': col_lbls[4],
	'font': lbls_font,
	'col_offset': label_col_offset(4),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[4], col_lbls[4]),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}

image_dict = {
	# 'moon':moon,
	'logo':logo,
	# 'labelbar':lbl_bar,
	'lbl0':lbl0,
	'lbl1':lbl1,
	'lbl2':lbl2,
	'lbl3':lbl3,
	'lbl4':lbl4,
}

# incompatible_fonts = [
# 	'emboss',
# 	'emboss2',
# 	'wideterm',
# 	'future',
# 	'pagga',
# 	'mono9',
# 	'bigmono9',
# 	'smmono9',
# 	'mono12',
# 	'bigmono12',
# 	'smmono12',
# 	'circle',
# 	'smblock',
# 	'smbraille'
# ]
