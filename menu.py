from asciimatics.screen import Screen
import time
import signal
import sys
import os
from menu_example_dict import menuexample
import socket

DEBUG = True

########### CONSTANTS #############
bgcolor = Screen.COLOUR_BLACK
textcolor = Screen.COLOUR_GREEN
textattrs = Screen.A_BOLD
logotext = 'HaLfWaY cRoOkS'
logolen = len(logotext)

########### GLOBALS ###############
logo_x = 0
logo_y = 0
logo_wrap_x = 0

########### CLASSES ###############
# class DimensionError(Exception):
# 	sys.exit()

class Panel():
	def __init__(self, screen, ulcx, ulcy, brcx, brcy, text=None):
		self.screen = screen
		self.ulcx = ulcx
		self.ulcy = ulcy
		self.brcx = brcx
		self.brcy = brcy
		self.tl = (self.ulcx, self.ulcy)
		self.tr = (self.brcx, self.ulcy)
		self.br = (self.brcx, self.brcy)
		self.bl = (self.ulcx, self.brcy)

		self.text = text 
		self.width = abs(brcx - ulcx)
		self.height = abs(brcy - ulcy)
		self.texth, self.textw = get_dict_h_w(text)

	def draw(self, thinline=False):
		self.screen.move(self.ulcx, self.ulcy)
		self.screen.draw(self.ulcx, self.brcy, colour=textcolor, thin=thinline) 	# Draw left border
		self.screen.move(self.ulcx, self.ulcy)
		self.screen.draw(self.brcx, self.ulcy, colour=textcolor, thin=thinline) 	# Draw top border
		self.screen.move(self.ulcx, self.brcy)
		self.screen.draw(self.brcx, self.brcy, colour=textcolor, thin=thinline) 	# Draw bottom border
		self.screen.move(self.brcx, self.ulcy)
		self.screen.draw(self.brcx, self.brcy, colour=textcolor, thin=thinline)	# Draw right border
		# TODO: add text


class Menu():
	def __init__(self, screen, menudict, startx, starty, endx, endy, thick=2):
		self.screen = screen
		self.menudict = menudict
		self.sx = startx
		self.ex = endx
		self.w = abs(endx - startx)

		self.sy = starty
		self.ey = endy
		self.h = abs(endy - starty)
		# ^TODO: ADJUST HEIGHT BASED ON len(self.menudict.values()) IF > self.h; CONSTRAIN TO SCREEN HEIGHT


		self.ncols = len(menudict) #numcols # == len(menudict.keys())
		self.thick = thick 			# Border line thickness

		## Corner coordinate pairs
		self.tl = (self.sx, self.sy)	# Top-left corner
		self.tr = (self.ex, self.sy)	# Top-right corner
		self.br = (self.ex, self.ey)	# Bottom-right corner
		self.bl = (self.sx, self.ey)	# Bottom-left corner
		self.cols = [] 
		self.make_cols()

	def make_cols(self):
		total_border_w = self.thick * (self.ncols + 1)
		per_col_w = (self.w // self.ncols) - total_border_w

		last_col_x = self.sx + self.thick 	# Starts at menu startx + border thickness
		# for n in range(self.ncols):
		for col_title in list(self.menudict.keys()):
			# TODO: adjust height (y-bounds) of panels based on len(), unless Menu.h adjusts properly on init
			# col_title = self.menudict.keys()[n]
			## Split each key-value entry in menudict into its own dict --> {'Title': ['Values',...]}
			col_text = {col_title : self.menudict[col_title]}
			col = Panel(self.screen, last_col_x, self.sy, last_col_x+per_col_w, self.ey, col_text)
			self.cols.append(col)
			last_col_x += col.brcx + self.thick
			# if (n == self.ncols-1) and (last_col_x > self.ex):
			# 	msg = "Column {} has exceeded allowed width for menu: max={}, actual={}".format(n,self.ex,last_col_x)
			# 	log_debug(msg)
				# raise DimensionError(msg)


	def draw(self):
		# outline = [self.tl, self.tr, self.br, self.bl]
		# polygon = [outline]
		draw_panel(self.screen, self.sx, self.sy, self.ex, self.ey)
		for col in self.cols:
			# polygon.append([col.tl, col.tr, col.br, col.bl])
			col.draw()

		# self.screen.fill_polygon(polygon, colour=textcolor, bg=bgcolor)


########### FUNCTIONS #######################

def cleanup(signum, stack):
	# ...
	#print('Goodbye!')
	# log_debug('SIGINT received: {}'.format(signum))
	sys.exit()

# def log_debug(msg,filename='debug.log'):
# 	print(msg)
# 	cmd = 'echo "{}" >> {}'.format(msg, filename)
# 	os.system(cmd)

def network_connected(host="8.8.8.8", port=53, timeout=3):
	"""
   Host: 8.8.8.8 (google-public-dns-a.google.com)
   OpenPort: 53/tcp
   Service: domain (DNS/TCP)
   """
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		# log_debug(ex.message)
		return False


def demo(screen):
	# panels = make_panels(screen)
	# log_debug('Demo begun! [{}]'.format(time.time()))

	## Verify network connection for fetching menu contents from Google Sheets; if none found, use menu_example_dict
	if network_connected() and not DEBUG:
		menucontents = getmenu.menu_dict()
	else:
		menucontents = menuexample
		
	menu = Menu(screen, menucontents, 2, 4, screen.width-2, screen.height-2, thick=1)

	while True:
		## For dynamic resizing of panels when screen dimensions are changed
		if screen.has_resized():
			# panels = make_panels(screen)
			menu = Menu(screen, menucontents, 2, 4, screen.width-2, screen.height-2, thick=1)

		screen.clear()
		scroll_logo(screen)

		menu.draw()

		# draw_panel(screen, screen.width // 5, screen.height // 5, int(screen.width * 0.8), int(screen.height * 0.8))
		# p1.draw()
		# p2.draw()
		# for p in panels:
		# 	p.draw()

		# screen.fill_polygon([
		# 	## Draw a filled polygon provided these (x,y) coordinate tuples for shape
		# 	[
		# 		(2, 0),
		# 		(70, 0),
		# 		(70, 10),
		# 		(60, 10)
		# 	],
		# 	## Additional nested lists of coordinates for cutting out holes within polygon
		# 	[
		# 		(63, 2),
		# 		(67, 2),
		# 		(67, 8),
		# 		(63, 8)
		# 	]
		# ], colour=textcolor, bg=bgcolor)

		screen.refresh()
		time.sleep(0.1)

def get_dict_h_w(d):
	ph = len(d.values())
	pw = 0
	for k in d.keys():
		if len(k) > pw:
			pw = len(k)
	for v in d.values():
		if len(v) > pw:
			pw = len(v)
	return ph, pw


## TODO: implement according to needs for menu columns (add more args -- all is currently hardcoded)
def make_panels(screen):
	p1_text = {'Make':['Lower', 'Var', 'Settings', 'Gleaner']}

	p1 = Panel(screen, 2, (screen.height // 10), int(screen.width//2)-2, int(screen.height//2)-2, p1_text)
	p2 = Panel(screen, p1.brcx, p1.ulcy, screen.width-2, p1.brcy, p1_text)
	# FIXME: ^ finish make_panels() to autogenerate list of panels w/ appropriate dimensions

	return [p1, p2]


def scroll_logo(screen):
	global logo_x, logo_y, logo_wrap_x
	if logo_y == 0:
		logo_y = 2
	# screen.print_at('HaLfWaY cRoOkS', screen.width // 2, screen.height // 2)
	# screen.clear()
	if logo_x == screen.width:
		logo_wrap_x = 0
	logo_x %= screen.width
	
	## Begin printing on left side of screen, starting with last character
	if logo_wrap_x < logolen:
		screen.print_at(logotext[logolen-logo_wrap_x-1:], 0, logo_y, textcolor, textattrs)
		logo_wrap_x += 1
	else:
		if logo_x == 0:
			logo_x += 1
		screen.print_at(logotext, logo_x, logo_y, textcolor, textattrs)
		logo_x += 1


## Takes in x,y coords for upper-left corner & bottom-right corner
def draw_panel(screen, ulcx, ulcy, brcx, brcy):
	screen.move(ulcx, ulcy)
	screen.draw(ulcx, brcy) 	# Draw left border
	screen.move(ulcx, ulcy)
	screen.draw(brcx, ulcy) 	# Draw top border
	screen.move(ulcx, brcy)
	screen.draw(brcx, brcy) 	# Draw bottom border
	screen.move(brcx, ulcy)
	screen.draw(brcx, brcy)		# Draw right border


if __name__ == '__main__':
	## Attach cleanup procedure for handling interrupt signals (i.e., KeyboardInterrupt)
	signal.signal(signal.SIGINT, cleanup)

	## Begin main program
	Screen.wrapper(demo)

