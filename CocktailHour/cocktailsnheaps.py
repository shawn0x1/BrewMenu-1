import pickle
import sys
import os
import curses
import time
import signal
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import TransportError
from httplib2 import ServerNotFoundError

DEBUG = False #True

########## Google Sheets API section #######################
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# LOGO_RANGE = 'A1:B1'
COL1_RANGE = 'A2:A14'
COL2_RANGE = 'B2:B14'
ranges = [COL1_RANGE, COL2_RANGE]
col_lbls = ['B&L Cocktails', 'Heaps']
sheet_url = "https://docs.google.com/spreadsheets/d/10NSm1MrEVvPW8rU-VovIqx5LTTbhriOBcYrcYDcKe6w/edit?ts=5ce61161#gid=0"
start_idx = sheet_url.index('/d/') + 3
end_idx = sheet_url.index('/edit')
SHEET_ID = sheet_url[start_idx:end_idx]

def log_debug(msg,filename='debug.log'):
	#print(msg)
	cmd = 'echo "{}" >> {}'.format(msg, filename)
	os.system(cmd)

def read_sheet(sheet, cells):
	return sheet.values().get(
						majorDimension='COLUMNS',
						spreadsheetId=SHEET_ID,
						range=cells,
						valueRenderOption='FORMULA'
						).execute().get('values', [])

def menu_dict():
	menu = dict.fromkeys(col_lbls, [])
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			try:
				creds = pickle.load(token)
			except UnicodeDecodeError:
				print("ERROR: Invalid token.pickle file, please re-authenticate at https://developers.google.com/sheets/api/quickstart/python")
				sys.exit(2)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			try:
				creds.refresh(Request())
			except TransportError:
				log_debug('TransportError caught: Failed to establish connection\n')
				sys.exit(2)
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
			creds = flow.run_local_server()
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	try:
		service = build('sheets', 'v4', credentials=creds) #, developerKey=API_KEY)
	except ServerNotFoundError:
		log_debug('ServerNotFoundError caught: Failed to establish connection\n')
		sys.exit(2)

	# Call the Sheets API
	sheet = service.spreadsheets()
	for i in range(len(col_lbls)):
		menu.update(
			{
				col_lbls[i] :
				read_sheet(sheet, ranges[i])
			}
		)
	return menu


########## Images & Art section ###################
logo_text = 'Halfway Crooks Cocktail Hour'  # Halfway Crooks Beer Cocktail Hour <-- really the tile, with Beer struckthrough
prompt_str = "sh-v4.4$ ./halfway_crooks.sh"
logofonts = ['big', 'script', 'shadow', 'slant', 'smascii12', 'standard']
logo_font = logofonts[3]
lblfonts = ['future', 'emboss', 'bubble', 'digital', 'mini', 'small', 'smscript', 'smslant', 'standard']
lbls_font = lblfonts[8] #5
WHITE = 0
BLACK = 1
GREEN = 3
art_dir = os.getcwd() + '/art/'

def get_art(font, text):
	if not os.path.isdir(art_dir):
		os.mkdir(art_dir)
	art = []
	split_text = text.strip().lower().split()
	key_idx = 0
	if len(split_text) > 1:
		if '&' in split_text[0] or split_text[0] == '-':
			key_idx = 1
	key = split_text[key_idx]
	art_file = art_dir + key + '_' + font + '_art.txt'
	if not os.path.isfile(art_file):
		os.system('figlet -t -f ' + font + ' ' + text + ' > ' + art_file)
	with open(art_file) as f:
		art = f.readlines()
	return art

def longest_str(image): 		# Determine max width of an ASCII art file   ## ENSURE THIS WORKS AS NEEDED
	max_len = 0
	# for line in image:
	# 	if len(str(line)) > max_len:
	# 		max_len = len(str(line))
	for item in enumerate(image):
		for s in item:
			if len(str(s)) > max_len:
				max_len = len(str(s))
	return max_len

########## Curses TUI section ########################
LOOP_SLEEP = 0.15
LINE_SPACE = 3
menu_rows_fit_error = False

menu_width = 0
menu_toprow = 0
logo_x = 0       # <-- formerly 'col_offset = terminal_width() - 1'
logo_end_x = 0
logo_y = 0
logo_img = None

def max_dimensions(window):
	height, width = window.getmaxyx()
	return height - 1, width

def divided_col_width(window, ncols):
	return max_dimensions(window)[1] // ncols

def create_panel(window, start_row, start_col, title, content, max_cols=5, content_color=GREEN, title_art_font=lbls_font):
	global menu_rows_fit_error
	panel = None
	title_art = get_art(title_art_font, title)
	title_art_lines = len(title_art)
	screen_height, screen_width = max_dimensions(window)
	panel_h = screen_height - start_row + 1 #3
	#while (start_row+panel_h) > (screen_height + 2):
	#	panel_h-=1
	panel_w = longest_str(content)
	if panel_w > divided_col_width(window, max_cols):
		panel_w = divided_col_width(window, max_cols)

	# if not FIT_SCREEN:
	# 	trim = max_dimensions(window)[1] // 20
	# 	panel_w -= int(trim)

	while (start_col+panel_w) > (screen_width):
		#panel_w -= 1
		start_col -= 1

	panel = window.derwin(panel_h, panel_w, start_row, start_col)
	if panel is None:
		return panel_w

	attr_list = [
		curses.A_BOLD,
		curses.A_UNDERLINE,
		#curses.A_STANDOUT,
		# curses.A_BLINK,
		# curses.A_HORIZONTAL,
		# curses.A_LEFT,
		# curses.A_LOW,
		# curses.A_VERTICAL,
	]
	attr = curses.color_pair(content_color)
	panel.attrset(attr)
	for a in attr_list:
		attr |= a
	#panel.attrset(attr)
	#panel.attrset(curses.color_pair(content_color))
	#panel.attroff(attr_list[])

	ls=curses.ACS_PLUS #LTEE
	rs=curses.ACS_PLUS #RTEE
	ts=curses.ACS_HLINE #curses.ACS_PLMINUS
	bs=curses.ACS_HLINE #'='
	tl=curses.ACS_ULCORNER
	tr=curses.ACS_URCORNER
	bl=curses.ACS_SSBB
	br=curses.ACS_LRCORNER
	panel.border(ls, rs, ts, bs, tl, tr, bl, br)
	#panel.border()

	inner_text_offset = 5  #3
	row_cnt = 1 #2
	top = title_art[0].strip()
	buff_cnt = 0
	while (len(top)+4) < panel_w:
		top = ' ' + top + ' '
		buff_cnt += 1

	for line in title_art:
		line = line.strip()
		startcol = int(buff_cnt*0.75) + (inner_text_offset//2)
		if lbls_font == 'small' or lbls_font == 'standard':
			if line == title_art[0].strip():
				startcol += 1
			elif line == title_art[len(title_art)-1].strip():
				startcol += 14
				if lbls_font == 'standard':
					startcol += 3
		panel.addstr(row_cnt, startcol, line, attr)
		row_cnt+=1
	#row_cnt+=1
	panel.addstr(row_cnt, inner_text_offset-1, '~'*((panel_w-inner_text_offset*2)+2)) #, attr)
	#row_cnt+=1

	item_cnt = 0
	for row, line in enumerate(content):
		for s in line:
			nottitle = s != title
			if len(title.split())>1 and title.split()[1] == s:
				nottitle = False
			if nottitle:
				if len(str(s)) > 1:
					row_cnt+=1
					if start_row+row+row_cnt < start_row+panel_h:
						#attr = (curses.A_BOLD | curses.A_UNDERLINE | curses.A_STANDOUT)
						if len(str(s)) == 0 or str(s)[0] == '-':
							panel.addstr(row+row_cnt, inner_text_offset, str(s).strip())
						else:
							panel.addstr(row+row_cnt, inner_text_offset, str(s).strip(), attr)
					else:
						menu_rows_fit_error = True
				row_cnt += (LINE_SPACE-1)

	panel.attrset(curses.color_pair(WHITE))
	return panel_w

def draw_menu(window, menu):
	global menu_width, menu_toprow
	ncols = len(menu.keys())
	next_col_y = len(logo_img) + 1 		# Represents height of logo art file
	next_col_x = 0 #1  #3
	# if not FIT_SCREEN:
	#     if menu_width > 0:
	#         next_col_x = int((max_dimensions(window)[1] - menu_width) / 2)
	offset = 0
	if DEBUG:
		k = col_lbls[0]
		offset = create_panel(window, next_col_y, next_col_x, k, menu.get(k), ncols)
		next_col_x += (offset - 1)
	else:
		for k in col_lbls:
			offset = create_panel(window, next_col_y, next_col_x, k, menu.get(k), ncols)
			next_col_x += (offset - 1)
	if menu_width == 0:
		menu_width = next_col_x
	if menu_toprow == 0:
		menu_toprow = next_col_y


LOGO_ON_SCREEN = 0
LOGO_WRAP_RIGHT = 1
LOGO_OFF_SCREEN = 2
LOGO_WRAP_LEFT = 3
states = [LOGO_ON_SCREEN,LOGO_WRAP_RIGHT,LOGO_OFF_SCREEN,LOGO_WRAP_LEFT]
logo_state = states[0]

def draw_logo(window, image, attrs=None):
	global logo_x, logo_end_x, logo_state, LOOP_SLEEP
	terminal_width = max_dimensions(window)[1]
	#start_column = terminal_width - logo_x
	
	if logo_state == LOGO_WRAP_LEFT and logo_x == 0 and 0 < logo_end_x < terminal_width:
		logo_state = LOGO_ON_SCREEN
		LOOP_SLEEP += 0.05

	elif logo_state == LOGO_ON_SCREEN and logo_x < terminal_width and logo_end_x >= terminal_width:
		logo_state = LOGO_WRAP_RIGHT

	elif logo_state == LOGO_WRAP_RIGHT and logo_x >= terminal_width:
		logo_state = LOGO_OFF_SCREEN
		return

	elif logo_state == LOGO_OFF_SCREEN:
		logo_state = LOGO_WRAP_LEFT
		logo_end_x = -3 #0
		LOOP_SLEEP -= 0.05
		return

	attr = curses.color_pair(GREEN)
	if attrs is not None:
		for a in attrs:
			attr |= a
	window.attrset(attr)
	## row will range from 1-6, column will range from 0-143 

	start_column = None #logo_x
	end_column = None #logo_end_x  #start_column + longest_str(image)
	first_col = None  ## THIS IS THE COLUMN INDEX TO BEGIN DRAWING FROM

	last_col = terminal_width  							# Dummy large value to initialize

	if logo_state == LOGO_ON_SCREEN or logo_state == LOGO_WRAP_RIGHT:  ## Use both logo_x & logo_end_x
		for row, line in enumerate(image, start=1):
			for column, symbol in enumerate(line, start=logo_x):
				if (column < terminal_width):
					window.addch(row+logo_y, column, symbol, attr)

	# elif logo_state == LOGO_WRAP_RIGHT:

	# elif logo_state == LOGO_OFF_SCREEN:	 ## Reset logo_x & logo_end_x positions

	elif logo_state == LOGO_WRAP_LEFT:  ## Begin drawing from logo_end_x = 0, set logo_x = 0 when logo_end_x == longest_str(img)-1
		if logo_end_x >= (longest_str(image) - 1):
			logo_x = -3 #0
		else:
			for row, line in enumerate(image, start=1):			# Start from 1 to leave row space for prompt_str
				last_col = len(line) - 1
				for column, symbol in enumerate(line, start=0):
					if (last_col - column) <= logo_end_x:
						window.addch(row+logo_y, column, symbol, attr)

	#if start_column < 0:
	#	start_column = 0
	#needtowrap = end_column > terminal_width
	
	###############
	# for row, line in enumerate(image, start=1):			# Start from 1 to leave row space for prompt_str
	# 	for column, symbol in enumerate(line, start=0):
	# 		cur_col = start_column + column
	# 		if cur_col == terminal_width-1:
	# 			last_col = column 	# All columns after this will need to be rendered starting back from 0
	# 		chr_x = cur_col
	# 		if column > last_col:	# Indicative that the text now must be wrapped
	# 			chr_x = column - last_col - 1
	# 			if chr_x < 0:
	# 				chr_x = 0
	# 		if column == len(line)-1:	# If last char in line, update global logo_end_x coordinate
	# 			logo_end_x = chr_x
	# 		try:
	# 			if chr_x <= terminal_width:
	# 				window.addch(row+logo_y, chr_x, symbol, attr)
	# 		except:
	# 			log_debug('needtowrap asserted: row={}, column={}, row+logo_y={}, chr_x={}, last_col={}, term_width={}, logo_x={}, start_column={}, end_column={}'.format(row,column,row+logo_y,chr_x,last_col,terminal_width,logo_x,start_column,end_column))
	# 			sys.exit(2)
	#################
	#else:
	#	for row, line in enumerate(image, start=1):
			## ^ If start=1, row==1 and increments each iteration
	#		for column, symbol in enumerate(line, start=start_column):
	#			if (column < terminal_width):
	#				window.addch(row+logo_y, column%terminal_width, symbol, attr)

	window.attrset(curses.color_pair(WHITE))

def scroll_logo(window, image):
	global logo_x, logo_end_x
	max_x = max_dimensions(window)[1] - 1
	#new_x = (logo_x-3) if (logo_x-3) > 0 else max_x
	# new_x = logo_x + 3
	# if new_x > max_x:		# Should increment logo_end_x by 3 here rather than in draw_logo?
	# 	if logo_end_x == longest_str(image)-1:
	# 		new_x = 0
	# logo_x = new_x
	logo_x += 3
	logo_end_x += 3

def main(window):
	global logo_img, menu_rows_fit_error, LINE_SPACE, logo_end_x
	curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.curs_set(0)
	menu = menu_dict()
	prompt_len = len(prompt_str)
	toggle_cursor = False
	toggle_char = '_'
	scroll_cnt = 0
	scroll_speed = 5
	logo_img = get_art(logo_font, logo_text)
	logo_end_x = logo_x + longest_str(logo_img)

	while True:
		scroll_cnt %= 100
		window.erase()
		window.addstr(0,1,prompt_str)
		if scroll_cnt % 2 == 0:
			toggle_char = '_' if toggle_cursor else ' '
			toggle_cursor = not toggle_cursor
		window.addch(0,1+prompt_len,toggle_char, curses.color_pair(WHITE))# | curses.A_BLINK)
		#window.addch(window.getmaxyx()[0]-1,1+prompt_len,toggle_char, curses.color_pair(WHITE))# | curses.A_BLINK)

		draw_logo(window, logo_img, attrs=[curses.A_BOLD]) #, curses.A_UNDERLINE]) #, curses.A_REVERSE]) #, curses.A_BLINK])
		draw_menu(window, menu)
		if menu_rows_fit_error:
			LINE_SPACE -= 1
			menu_rows_fit_error = False

		if scroll_cnt % scroll_speed == 0:
			scroll_logo(window, logo_img)

		window.refresh()
		time.sleep(LOOP_SLEEP)
		scroll_cnt += 1

def cleanup(signum, stack):
	sys.exit(2)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, cleanup)
	curses.wrapper(main)
