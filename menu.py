#!/usr/bin/python3
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

RPI=0
UBUNTU=1
MACOSX=2

CONTROL_OS = RPI #MACOSX

SHOW_BEERS_WIDETERM = True and (CONTROL_OS != RPI)
SHOW_HEAPS_WIDETERM = True and (CONTROL_OS != RPI)

DEBUG = False #True

########## Google Sheets API section #######################
try:
	FILEPATH = (os.environ['HOME'] + '/BrewMenu/') if CONTROL_OS!=MACOSX else (os.environ['HOME'] + '/Documents/BrewMenu/')
except KeyError:
	FILEPATH = '/home/halfway/BrewMenu/'
CREDFILE = FILEPATH + 'credentials.json'
TOKENFILE = FILEPATH + 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# LOGO_RANGE = 'A1:B1'
#COL1_RANGE = 'A2:A14'
#COL2_RANGE = 'B2:B14'
#ranges = [COL1_RANGE, COL2_RANGE]
# beers_ranges = ['beers!A2:A17', 'beers!B2:B17', 'beers!C2:C17', 'beers!D2:D17', 'beers!E2:E17']		#'beers!A2:E17'
beers_ranges1 = ['beers!A3:A10', 'beers!B3:B10', 'beers!C3:C10', 'beers!D3:D10', 'beers!E3:E10']
beers_ranges2 = ['beers!A11:A17', 'beers!B11:B17', 'beers!C11:C17', 'beers!D11:D17', 'beers!E11:E17']
beers_ranges1_raw = ('A3:A10', 'B3:B10', 'C3:C10', 'D3:D10', 'E3:E10')
beers_ranges2_raw = ('A11:A17', 'B11:B17', 'C11:C17', 'D11:D17', 'E11:E17')
beers_col_lbls = ('Name', 'Type', 'ABV', 'Pour', 'Cost')
# heaps_range = 'heaps!A1:A24'
# heaps_ranges = ('heaps!A2:A4', 'heaps!A7:A10', 'heaps!A13:A16', 'heaps!A19:A24')
heaps_ranges = ('food!A2:A7', 'food!A10:A12', 'food!A15:A18')
heaps_ranges_raw = ('A2:A4', 'A7:A10', 'A13:A16', 'A19:A24')
# heaps_col_lbls = ('Double Fried Belgian Fries', 'Cheese', 'Meat', 'Heaps Savory New Zealand Pies and Rolls')
heaps_col_lbls = ('Heaps Pies', 'Fries', 'Cheese')


sheet_url = "https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=0"
beers_url = 'https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=0'
heaps_url = 'https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=1702929798'

def extract_id(url):
	start = url.index('/d/') + 3
	end = url.index('/edit')
	return url[start:end]

SHEET_ID = extract_id(sheet_url)
BEERS_ID = extract_id(beers_url)
HEAPS_ID = extract_id(heaps_url)

def log_debug(msg,filename=str(FILEPATH+'debug.log')):
	#print(msg)
	cmd = 'echo "{}" >> {}'.format(msg, filename)
	os.system(cmd)



def read_sheet(sheet, cells, sid=SHEET_ID): # url=sheet_url):
	# sid = extract_id(url)
	return sheet.values().get(
						majorDimension='COLUMNS',
						spreadsheetId=sid,
						range=cells,
						valueRenderOption='FORMULA'
						).execute().get('values', [])

def validate_service():
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists(TOKENFILE):
		with open(TOKENFILE, 'rb') as token:
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
			flow = InstalledAppFlow.from_client_secrets_file(CREDFILE, SCOPES)
			creds = flow.run_local_server()
		# Save the credentials for the next run
		with open(TOKENFILE, 'wb') as token:
			pickle.dump(creds, token)
	try:
		service = build('sheets', 'v4', credentials=creds) #, developerKey=API_KEY)
	except ServerNotFoundError:
		log_debug('ServerNotFoundError caught: Failed to establish connection\n')
		sys.exit(2)
	return service

def parse(vals): 		# For currency and percentage values
	retvals = []
	for v in vals:
		subvals = []
		for vv in v:
			if isinstance(vv, str):
				subvals.append(vv.replace('~dollar~', '$'))
			elif isinstance(vv, float):
				subvals.append('{:.1f}%'.format(vv*100))
			else:
				subvals.append(vv)
		retvals.append(subvals)	
	return retvals

def menu_dict():
	beer_menu1 = dict.fromkeys(beers_col_lbls, [])
	beer_menu2 = dict.fromkeys(beers_col_lbls, [])
	heaps_menu = dict.fromkeys(heaps_col_lbls, [])
	
	# Call the Sheets API
	service = validate_service()
	sheet = service.spreadsheets()
	
	for i in range(len(beers_col_lbls)):
		beer_menu1.update(
			{
				beers_col_lbls[i] : parse(read_sheet(sheet, beers_ranges1_raw[i], sid=BEERS_ID))
			}
		)
	for i in range(len(beers_col_lbls)):
		beer_menu2.update(
			{
				beers_col_lbls[i] : parse(read_sheet(sheet, beers_ranges2_raw[i], sid=BEERS_ID))
				
			}
		)
	for i in range(len(heaps_col_lbls)):
		heaps_menu.update(
			{
				heaps_col_lbls[i] : parse(read_sheet(sheet, heaps_ranges[i], sid=HEAPS_ID)) 
				
			}
		)
	return (beer_menu1, beer_menu2, heaps_menu)


########## Images & Art section ###################
logo_text = 'Halfway Crooks' # :: Brews && Blends'
prompt_str = "sh-v4.4$ ./halfway_crooks.sh"
logofonts = ['big', 'script', 'shadow', 'slant', 'smascii12', 'standard']
logo_font = 'standard' #'letter' #logofonts[3]
lblfonts = ['future', 'emboss', 'bubble', 'digital', 'mini', 'small', 'smscript', 'smslant', 'standard']
beers_lbls_font = 'pagga' #lblfonts[2] #5
heaps_lbls_font = 'term' #lblfonts[5]
WHITE = 0
BLACK = 1
GREEN = 3


# if CONTROL_OS == RPI or CONTROL_OS == UBUNTU:
# 	art_dir = os.environ['HOME'] + '/BrewMenu/art/'
# else:
# 	art_dir = os.environ['HOME'] + '/Documents/BrewMenu/art/'

art_dir = FILEPATH + 'art/'

def get_art(font, text):
	if not os.path.isdir(art_dir):
		os.mkdir(art_dir)
	art = []
	split_text = text.strip().lower().split()
	key_idx = 0
	is_currency = False
	if len(split_text) > 1:
		if '&' in split_text[0] or '$' in split_text[0]:
			key_idx = 1
	elif '$' in split_text[0]:
		# split_text[0] = split_text[0].replace('$','d')
		split_text[0] = split_text[0].replace('$',"\$")
		is_currency = True
	if not is_currency:
		key = split_text[key_idx]
	else:
		key = 'd'+split_text[key_idx][2]
		text = text.replace('$', '"\$"')
	if '/' in key:
		key = key.replace('/', '')
	art_file = art_dir + key + '_' + font + '_art.txt'
	if not os.path.isfile(art_file):
		# print(art_file + ' Does not exist, trying figlet...')
		# os.system('figlet -tk -f ' + font + ' "' + text + '" > ' + art_file)
		if font == 'wideterm':
			os.system('figlet -tS -f ' + font + ' "' + text + '" > ' + art_file)
		else:
			os.system('figlet -t -f ' + font + ' "' + text + '" > ' + art_file)
	if not os.path.isfile(art_file) or os.stat(art_file).st_size == 0:
		# print(art_file + ' Does not exist, trying toilet...')
		# os.system('toilet -tk -f ' + font + ' "' + text + '" > ' + art_file)
		if font == 'wideterm':
			os.system('toilet -tS -f ' + font + ' "' + text + '" > ' + art_file)
		else:
			os.system('toilet -t -f ' + font + ' "' + text + '" > ' + art_file)
	with open(art_file) as f:
		art = f.readlines()
	return art

def longest_str(image): 		# Determine max width of an ASCII art file   ## ENSURE THIS WORKS AS NEEDED
	max_len = 0
	if image:
		try:
			for item in enumerate(image):
				for s in item:
					if len(str(s)) > max_len:
						max_len = len(str(s))
		except TypeError:
			for line in image:
				if len(str(line)) > max_len:
					max_len = len(str(line))
	return max_len

########## Curses TUI section ########################
LOOP_SLEEP = 0.25  #0.15
LINE_SPACE = 3
menu_rows_fit_error = False

menu_width = 0
menu_toprow = 0
logo_x = 20 #0       # <-- formerly 'col_offset = terminal_width() - 1'
logo_end_x = 0
logo_y = 0
logo_img = None

LOGO_ON_SCREEN = 0
LOGO_WRAP_RIGHT = 1
LOGO_OFF_SCREEN = 2
LOGO_WRAP_LEFT = 3
logo_state_list = [LOGO_ON_SCREEN,LOGO_WRAP_RIGHT,LOGO_OFF_SCREEN,LOGO_WRAP_LEFT]
logo_state = logo_state_list[0]

BEERS1 = 0
BEERS2 = 1
HEAPS = 2
menu_state_list = [BEERS1, BEERS2, HEAPS]
menu_state = menu_state_list[0]
MENU_CHANGE_PERIOD = 10

def max_dimensions(window):
	height, width = window.getmaxyx()
	return height - 1, width

def divided_col_width(window, ncols):
	return max_dimensions(window)[1] // ncols

def divided_row_height(window, nrows):
	return max_dimensions(window)[0] // nrows

def create_beers_panel(window, start_row, start_col, title, content, max_cols=5, content_color=GREEN, title_art_font=beers_lbls_font):
	global menu_rows_fit_error
	panel = None
	title_art = get_art(title_art_font, title)
	title_art_lines = len(title_art)
	screen_height, screen_width = max_dimensions(window)
	panel_h = screen_height - start_row + 1 #3

	panel_w = longest_str(content) + 2
	if panel_w < longest_str(title_art)+2:
		panel_w = longest_str(title_art)+2
	# if panel_w > divided_col_width(window, max_cols):
	panel_w = divided_col_width(window, max_cols)

	# if not FIT_SCREEN:
	# 	trim = max_dimensions(window)[1] // 20
	# 	panel_w -= int(trim)

	while (start_col+panel_w) > (screen_width):
		#panel_w -= 1
		start_col -= 1
	try:
		panel = window.derwin(panel_h, panel_w, start_row, start_col)
	except:
		return panel_w 
	if panel is None:
		return panel_w

	attr_list = [
		curses.A_BOLD,
		# curses.A_UNDERLINE,
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
		#startcol = int(buff_cnt*0.75) + (inner_text_offset//3)
		startcol = int(buff_cnt) + (inner_text_offset//3)
		if title_art_font == 'small' or title_art_font == 'standard':
			if line == title_art[0].strip():
				startcol += 1
			elif line == title_art[len(title_art)-1].strip():
				startcol += 14
				if title_art_font == 'standard':
					startcol += 3
		elif title_art_font == 'future' and title.lower() == 'type':
			if line != title_art[0].strip():
				startcol += 1
		panel.addstr(row_cnt, startcol, line, attr)
		row_cnt+=1
	row_cnt+=1
	panel.addstr(row_cnt, inner_text_offset-1, '~'*((panel_w-inner_text_offset*2)+2)) #, attr)
	row_cnt+=1

	inner_text_offset -= 3
	item_cnt = 0
	if content:
		for row, line in enumerate(content):
			# log_debug(line, )
			# s_img = get_art('wideterm', line)
			for s in line:
				nottitle = s != title
				if len(title.split())>1 and title.split()[1] == s:
					nottitle = False
				if nottitle:
					# s_img = get_art('wideterm', s)
					if len(str(s)) > 1:
						row_cnt+=1
						if start_row+row+row_cnt < start_row+panel_h:
							#attr = (curses.A_BOLD | curses.A_UNDERLINE | curses.A_STANDOUT)

							if not SHOW_BEERS_WIDETERM:
								## With contents as plaintext:
								if len(str(s)) == 0 or str(s)[0] == '-':
									panel.addstr(row+row_cnt, inner_text_offset, str(s).strip())
								else:
									panel.addstr(row+row_cnt, inner_text_offset, str(s).strip(), attr)
							else:
								## With contents as figlet image files:
								s_img = get_art('wideterm', s)
								for r in s_img:
									panel.addstr(row+row_cnt, inner_text_offset, r, attr)
									row_cnt += 1

						else:
							menu_rows_fit_error = True
					row_cnt += (LINE_SPACE-1)

	panel.attrset(curses.color_pair(WHITE))
	return panel_w

def create_heaps_panel(window, start_row, start_col, title, content, max_rows=4, content_color=GREEN, title_art_font=heaps_lbls_font):
	panel = None
	title_art = get_art(title_art_font, title)
	title_art_lines = len(title_art)

	screen_height, screen_width = max_dimensions(window)
	"""
	panel_h = screen_height - start_row + 1 #3
	div_h = divided_row_height(window, max(max_rows, len(content))) #- 2
	# if len(content) < 4:
	# 	div_h -= 1
	if panel_h > div_h:
		panel_h = div_h
	if panel_h < len(content):
		panel_h = len(content)+3
	"""
	panel_h = len(content[0]) + 5 #7 #6 #4

	# panel_w = longest_str(content)
	panel_w = screen_width - 2

	while (start_col+panel_w) > (screen_width):
		#panel_w -= 1
		start_col -= 1
	try:
		panel = window.derwin(panel_h, panel_w, start_row, start_col)
	except:
		return panel_w 
	if panel is None:
		return panel_w

	attr_list = [
		curses.A_BOLD,
		# curses.A_UNDERLINE,
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

	inner_text_offset = 3 #5 
	row_cnt = 1 #2
	top = title_art[0].strip()
	buff_cnt = 0
	while (len(top)+4) < panel_w:
		top = ' ' + top + ' '
		buff_cnt += 1

	for line in title_art:
		line = line.strip()
		startcol = int(buff_cnt) + (inner_text_offset//3)
		if title_art_font == 'small' or title_art_font == 'standard':
			if line == title_art[0].strip():
				startcol += 1
			elif line == title_art[len(title_art)-1].strip():
				startcol += 14
				if title_art_font == 'standard':
					startcol += 3
		panel.addstr(row_cnt, startcol, line, attr|curses.A_BOLD|curses.A_UNDERLINE)
		row_cnt+=1
	row_cnt+=1
	panel.addstr(row_cnt, inner_text_offset-1, '~'*((panel_w-inner_text_offset*2)+2)) #, attr)
	#row_cnt+=1

	# item_cnt = 0
	if content:
		# inner_text_offset = panel_w // 4
		## TODO: Maybe try to center text?
		for row, line in enumerate(content):
			item_cnt = 0
			for s in line:
				nottitle = s != title
				if len(title.split())>1 and title.split()[1] == s:
					nottitle = False
				if nottitle:
					if len(str(s)) > 1:
						row_cnt+=1
						if start_row+row+row_cnt < start_row+panel_h:
							#attr = (curses.A_BOLD | curses.A_UNDERLINE | curses.A_STANDOUT)
							
							if not SHOW_HEAPS_WIDETERM:
								## Writing contents as plaintext:
								if item_cnt > 0:
									panel.addstr(row+row_cnt, inner_text_offset+4, str(s).strip(), attr)
								else:
									panel.addstr(row+row_cnt, inner_text_offset, str(s).strip(), attr | curses.A_UNDERLINE)
							else:
								## Writing contents as figlet image file:
								s_img = get_art('wideterm', s)
								if item_cnt > 0:
									for r in s_img:
										try:
											panel.addstr(row+row_cnt, inner_text_offset+4, r, attr)
										except:
											log_debug(r, 'heap_addstr.err')
											sys.exit()
										row_cnt+=1
								else:
									for r in s_img:
										panel.addstr(row+row_cnt, inner_text_offset, r, attr | curses.A_UNDERLINE)
										row_cnt+=1

						else:
							menu_rows_fit_error = True
						item_cnt += 1
					# row_cnt += (LINE_SPACE-1)

	panel.attrset(curses.color_pair(WHITE))
	return panel_h

### TODO: Show all menu contents as images in wideterm font

def draw_menu(window, menu):
	global menu_width, menu_toprow
	nkeys = len(menu.keys())
	next_y = len(logo_img) + 1 		# Represents height of logo art file
	next_x = 0 #1  #3
	# if not FIT_SCREEN:
	#     if menu_width > 0:
	#         next_col_x = int((max_dimensions(window)[1] - menu_width) / 2)
	offset = 0
	# if DEBUG:
	# 	k = beers_col_lbls[0]
	# 	offset = create_panel(window, next_col_y, next_col_x, k, menu.get(k), ncols)
	# 	next_col_x += (offset - 1)
	# else:
		# labels = beers_col_lbls if menu_state != HEAPS else heaps_col_lbls
		# for k in labels:
		# 	offset = create_panel(window, next_col_y, next_col_x, k, menu.get(k), ncols)
		# 	next_col_x += (offset - 1)

	if menu_state == HEAPS:
		# log_debug(menu, 'heaps_menu.log')
		for k in heaps_col_lbls:
			offset = create_heaps_panel(window, next_y, next_x, k, menu.get(k), nkeys)
			next_y += (offset)
	else:
		for k in beers_col_lbls:
			offset = create_beers_panel(window, next_y, next_x, k, menu.get(k), nkeys)
			next_x += (offset - 1)

	if menu_width == 0:
		menu_width = next_x
	if menu_toprow == 0:
		menu_toprow = next_y



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

	window.attrset(curses.color_pair(WHITE))

def scroll_logo(window, image):
	global logo_x, logo_end_x
	max_x = max_dimensions(window)[1] - 1
	logo_x += 3
	logo_end_x += 3


def main(window):
	global logo_img, menu_rows_fit_error, LINE_SPACE, logo_end_x, menu_state #, menu_state_timestamp
	curses.start_color()
	curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.curs_set(0)
	menu_opts = menu_dict()
	prompt_len = len(prompt_str)
	toggle_cursor = False
	toggle_char = '_'
	scroll_cnt = 0
	scroll_speed = 7  #5
	logo_img = get_art(logo_font, logo_text)
	logo_end_x = logo_x + longest_str(logo_img)

	menu_state_timestamp = time.time()

	while True:
		scroll_cnt %= 100
		window.erase()
		# window.addstr(2,2,str(scroll_cnt),curses.color_pair(WHITE))
		window.addstr(0,1,prompt_str)
		if scroll_cnt % 2 == 0:
			toggle_char = '_' if toggle_cursor else ' '
			toggle_cursor = not toggle_cursor
		window.addch(0,1+prompt_len,toggle_char, curses.color_pair(WHITE))# | curses.A_BLINK)
		#window.addch(window.getmaxyx()[0]-1,1+prompt_len,toggle_char, curses.color_pair(WHITE))# | curses.A_BLINK)

		if scroll_cnt % scroll_speed != 0:
			draw_logo(window, logo_img, attrs=[curses.A_BOLD]) #, curses.A_UNDERLINE]) #, curses.A_REVERSE]) #, curses.A_BLINK])

		if time.time() - menu_state_timestamp >= MENU_CHANGE_PERIOD:
			menu_state_timestamp = time.time()
			menu_state = (menu_state + 1) % len(menu_state_list)
		# state = menu_state_list[menu_state]

		## FOR DEBUG:
		# menu_state = HEAPS 

		menu = menu_opts[menu_state]
		if not any(menu.values()):
			menu_state_timestamp = time.time()
			menu_state = (menu_state + 1) % len(menu_state_list)
			menu = menu_opts[menu_state]
		draw_menu(window, menu)

		# if menu_rows_fit_error:
		# 	LINE_SPACE -= 1
		# 	menu_rows_fit_error = False

		#if scroll_cnt % scroll_speed == 0:
		#	scroll_logo(window, logo_img)

		window.refresh()
		time.sleep(LOOP_SLEEP)
		scroll_cnt += 1


def cleanup(signum, stack):
	sys.exit(2)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, cleanup)
	# curses.wrapper(main)
	try:
		scr = curses.initscr()
	except _curses.error:
		import subprocess
		subprocess.call(['lxterminal', '--command', 'python3', __file__])
	else:
		main(scr)
