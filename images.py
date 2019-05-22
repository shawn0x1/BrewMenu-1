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


class Cell(object):
	def __init__(self, window, name, start_y, start_x, height, width, contents, color_code=2, fg_color=2, bg_color=0):
		self.window = window
		self.name = name
		self.start_y = start_y
		self.end_y = start_y + height
		self.height =  height
		self.start_x = start_x
		self.end_x = start_x + width
		self.width = width
		self.contents = contents
		self.color_code = color_code
		self.fg_color = fg_color
		self.bg_color = bg_color
		self.cell = None

	def draw(self):
		# pass
		# window.subwin(nlines, ncols, begin_y, begin_x)
		# self.cell = curses.newwin(self.height, self.width, self.start_y, self.start_x)
		try:
			# self.cell = self.window.subwin(self.height+4,self.width, self.start_y, self.start_x)
			# self.cell = self.window.derwin(self.height+2, self.width, 5, 1)
			self.cell = self.window.subwin(len(self.contents)+1, self.width, 5, 1)
		except:
			print("Box dimensions out of bounds of parent window")
		# curses.box(self.cell)
		if self.cell is None:
			draw_error_window(self.window, x=5)
			draw_error_window(self.window, x=15-1)
			return
		self.cell.box()
		line_height = 1
		row_count = 1
		""" NOTE: addstr x & y dims are relative to the box border, not parent window!!! """
		self.cell.addstr(row_count, 1, self.name)
		row_count+=1
		self.cell.addstr(row_count, 1, "-"*(self.width-2))
		for i in range(len(self.contents)):
			row_count+=1
			self.cell.addstr(row_count, 1, self.contents[i])
		# for i in range(self.height):
		# 	row_count += 1
		# 	# try:
		# 	self.cell.addstr(self.start_y+row_count, self.start_x, str(self.contents[i]))
			# except:
			# 	continue

# class ColumnTop(Cell):
# 	def draw(self):
# 		super().draw()



# class ColumnMid(Cell):
# 	def draw(self):
# 		super().draw()


# prev_col_offset = terminal_width() - 10
# prev_row_offset = terminal_height() - 16
drawn_columns = {}

class Column(object):
	prev_col_x = 0

	def __init__(self, window, title, content, x=0, y=16):
		# global prev_col_offset
		# global prev_row_offset
		# prev_col_offset = terminal_width() - 10
		# prev_row_offset = terminal_height() - 16
		global drawn_columns
		if not title in drawn_columns.keys():
			self.title = title
			self.width = longest_str(content)+4 #[0] + 4
			self.height = len(content)
			self.content = content
			start_x = x + Column.prev_col_x
			start_y = y
			self.header = Cell(window, self.title, start_y, start_x, self.height, self.width, self.content)
			# prev_col_offset -= self.width
			# self.rows = [self.header]
			# for i in range(1, height):
			# 	self.rows.append()
			# self.header.draw()

			drawn_columns.update({self.title : self.header})
			Column.prev_col_x += self.width

	def draw(self, x=0):
		if x > 0:
			self.header.start_x += x
			self.header.end_x = self.header.start_x + self.width
		self.header.draw()



## Takes string, title, and a list of content strings
# def render_column(title, content):
	# global prev_col_offset


# def update_offset(ncols):




art_dir = os.getcwd() + '/ascii_art'
file_dict = {}

# Must `sudo apt-get install toilet` on the host system
def get_art(font, text, key, usetoilet=False):
	art = []
	if not os.path.isdir(art_dir):
		os.mkdir(art_dir)
	key = key.replace(' ', '_')
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
	'text': get_art(logo_font, logo_title, 'logo') if not IMGFROMFILE else load_from_file(LOGOFILE),
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

def label_bar_text():
	space = terminal_width() / (len(col_lbls) * 2) + 4
	# make = '{:{ali'
	bar = '|{:_^{space}}|{:_^{space}}|{:_^{space}}|{:_^{space}}|{:_^{space}}|'.format(col_lbls[0],col_lbls[1],col_lbls[2],col_lbls[3],col_lbls[4],space=space)
	# for i in range(len(col_lbls)):
	# 	bar = bar + ' '*10  #*label_col_offset(0)
	# 	bar = bar + col_lbls[i]
	# 	bar = bar + ' ||'
	# os.system('echo '+bar+' > gui_log.txt')
	return bar
	# return '||   %s   ||   %s   ||   %s   ||   %s   ||   %s   ||' % (col_lbls[0], col_lbls[1],col_lbls[2],col_lbls[3],col_lbls[4])

lbl_bar = {
	# 'label': 'labelbar',
	'key': 'labelbar',
	'font': lbls_font,
	'col_offset': terminal_width() - 1, #label_col_offset(0),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, label_bar_text(), 'labelbar'),
	# 'text': get_art(lbls_font, "|Make|Type|ABV|Pour|Cost|", 'labelbar'),
	'color': color_codes['RED'], #['GREEN'],
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}

lbl0 = {
	'key': col_lbls[0],
	'font': lbls_font,
	'col_offset': label_col_offset(0),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[0], 'lbl%d'%0),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl1 = {
	'key': col_lbls[1],
	'font': lbls_font,
	'col_offset': label_col_offset(1),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[1], 'lbl%d'%1),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl2 = {
	'key': col_lbls[2],
	'font': lbls_font,
	'col_offset': label_col_offset(2),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[2], 'lbl%d'%2),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl3 = {
	'key': col_lbls[3],
	'font': lbls_font,
	'col_offset': label_col_offset(3),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[3], 'lbl%d'%3),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}
lbl4 = {
	'key': col_lbls[4],
	'font': lbls_font,
	'col_offset': label_col_offset(4),
	'row_offset': lbls_row_offset,
	'text': get_art(lbls_font, col_lbls[4], 'lbl%d'%4),
	'color': lbls_color,
	'fg': COLOR_GREEN,
	'bg': COLOR_BLACK
}

# moon_text = [
# 		'          ',
# 		'          ',
# 		'          ',
# 		'          ',
# 		'          ',
# 		' **       ',
# 		'  ***     ',
# 		'   ***    ',
# 		'    ****  ',
# 		'     **** ',
# 		'     **** ',
# 		'     ***  ',
# 		'    ***   ',
# 		'  ***     ',
# 		' **       ',
# 	]
# moon = {
# 	'text': moon_text,
# 	'font': None,
# 	'col_offset': 10,
# 	'row_offset': 0,
# 	'color': color_codes['YELLOW'],
# 	'fg': COLOR_YELLOW,
# 	'bg': COLOR_BLACK
# 	}

image_dict = {
	# 'moon':moon,
	'logo':logo,
	'labelbar':lbl_bar,
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
