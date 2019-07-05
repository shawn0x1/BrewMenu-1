#!/usr/bin/python3
import pickle
import json
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

SHOW_BEERS_WIDETERM = False #True and (CONTROL_OS != RPI)
SHOW_HEAPS_WIDETERM = False #True and (CONTROL_OS != RPI)

DEBUG_BEER = False
beer_debug_file = 'beer_menu.debug'
DEBUG_HEAPS = False
food_debug_file = 'food_menu.debug'
DEBUG_MERCH = False
merch_debug_file = 'merch_menu.debug'

########## Google Sheets API section #######################
try:
	FILEPATH = (os.environ['HOME'] + '/BrewMenu/') if CONTROL_OS!=MACOSX else (os.environ['HOME'] + '/Documents/BrewMenu/')
except KeyError:
	FILEPATH = '/home/halfway/BrewMenu/'

CREDFILE = FILEPATH + 'credentials.json'
TOKENFILE = FILEPATH + 'token.pickle'

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

## TODO: Intelligently read in && set column labels rather than hardcoding...

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

merch_ranges = ('merch!A3:A7', 'merch!B3:B7')
merch_cols = ('Item', 'Cost')

sheet_url = "https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=0"
beers_url = 'https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=0'
heaps_url = 'https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=1702929798'
merch_url = 'https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=1883950632'

def extract_id(url):
	start = url.index('/d/') + 3
	end = url.index('/edit')
	return url[start:end]

SHEET_ID = extract_id(sheet_url)
BEERS_ID = extract_id(beers_url)
HEAPS_ID = extract_id(heaps_url)
MERCH_ID = extract_id(merch_url)

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
			elif vv == 0 or vv == 0.0:
				subvals.append('{:.1f}%'.format(vv))
			else:
				subvals.append(vv)
		retvals.append(subvals)
	return retvals

def menu_dict():
	beer_menu1 = dict.fromkeys(beers_col_lbls, [])
	beer_menu2 = dict.fromkeys(beers_col_lbls, [])
	heaps_menu = dict.fromkeys(heaps_col_lbls, [])
	merch_menu = dict.fromkeys(merch_cols, [])
	
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
	for i in range(len(merch_cols)):
		merch_menu.update(
			{
				merch_cols[i] : parse(read_sheet(sheet, merch_ranges[i], sid=MERCH_ID))
			}
		)
	menu_opts = (beer_menu1, beer_menu2, heaps_menu, merch_menu)
	for opt in menu_opts:
		if any(opt.values()):
			for idx, key in enumerate(opt.keys()):
				opt.update({key : opt[key][0]})
	return menu_opts


########## Images & Art section ###################
logo_text = 'Halfway Crooks' # :: Brews && Blends'
prompt_str = "sh-v4.4$ ./halfway_crooks/{}.sh"
logofonts = ['big', 'script', 'shadow', 'slant', 'smascii12', 'standard', 'mono9']
logo_font = 'slant' #'standard'  #logofonts[3]
lblfonts = ['future', 'emboss2', 'bubble', 'digital', 'mini', 'small', 'smscript', 'smslant', 'standard']
#heaps_fit_err_cnt = 0
#alt_heaps_lbl_fonts = ['emboss2', 'future', 'small', 'smslant', 'smshadow']
beers_lbls_font = 'pagga' #lblfonts[2] #5
heaps_lbls_font = 'pagga' #lblfonts[5]
merch_lbl_font = 'letter'  #'banner'
merch_header_text = '* * M E R C H * *'
WHITE = 0
BLACK = 1
GREEN = 3


art_dir = FILEPATH + 'art/'

def get_art(font, text):
	if not os.path.isdir(art_dir):
		os.mkdir(art_dir)
	art = []
	split_text = text.strip().lower().split()
	key_idx = 0
	is_currency = False
	if len(split_text) > 1:
		special_chars = ['&', '$', '*']
		if any(char in split_text[0] for char in special_chars):
			key_idx = 1
			if any(char in split_text[1] for char in special_chars):
				key_idx = 2
	elif '$' in split_text[0]:
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
	t_flag = '-t' if font != 'wideterm' else '-tS'
	if not os.path.isfile(art_file):
		os.system('figlet ' + t_flag + ' -f ' + font + ' "' + text + '" > ' + art_file)
	if not os.path.isfile(art_file) or os.stat(art_file).st_size == 0:
		os.system('toilet ' + t_flag + ' -f ' + font + ' "' + text + '" > ' + art_file)
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
CENTER_MENU_TEXT = True

beers_init = False
change_set_menu_width = 0
menu_width = 0
beer_panel_w_delta = 0

heaps_init = False
change_set_menu_height = 0
menu_height = 0
heaps_panel_h_delta = 0
HEAPS_LABELS_AS_IMGS = True

RIGHT_ALIGN = 0xA
LEFT_ALIGN  = 0xB
CENTER_ALIGN = 0xC
food_alignment = RIGHT_ALIGN

## TODO: ^ Add alignment configurations for beer && merch menus

CENTER_LOGO = False
menu_toprow = 0
logo_x = 0       # <-- formerly 'col_offset = terminal_width() - 1'
logo_end_x = 0
logo_y = 0
logo_img = None

LOGO_SCROLL = False
LOGO_ON_SCREEN = 0
LOGO_WRAP_RIGHT = 1
LOGO_OFF_SCREEN = 2
LOGO_WRAP_LEFT = 3
logo_state_list = [LOGO_ON_SCREEN,LOGO_WRAP_RIGHT,LOGO_OFF_SCREEN,LOGO_WRAP_LEFT]
logo_state = logo_state_list[0]

BEERS1 = 0
BEERS2 = 1
HEAPS = 2
MERCH = 3
menu_state_list = [BEERS1, BEERS2, HEAPS, MERCH]
menu_state = menu_state_list[0]
MENU_CHANGE_PERIOD = 17

## Border chars for panels (set in main):
ls=None
rs=None
ts=None
bs=None 
tl=None 
tr=None 
bl=None
br=None 

def max_dimensions(window):
	height, width = window.getmaxyx()
	return height - 1, width

def divided_col_width(window, ncols):
	return max_dimensions(window)[1] // ncols

def divided_row_height(window, nrows):
	return max_dimensions(window)[0] // nrows


def create_beers_panel(window, start_row, start_col, title, content, max_cols=5, content_color=GREEN, title_art_font=beers_lbls_font):
	global menu_rows_fit_error, change_set_menu_width, beer_panel_w_delta, beers_init
	panel = None
	title_art = get_art(title_art_font, title)
	title_art_lines = len(title_art)
	screen_height, screen_width = max_dimensions(window)
	screen_width += 1
	if title.lower() == 'name':
		start_col += 2
	panel_h = screen_height - start_row + 1 #3

	panel_w = 0
	for item in content:
		width = len(str(item))
		if width > panel_w:
			panel_w = width
	panel_w += 2 #4
	if panel_w < longest_str(title_art)+2: #4:
		panel_w = longest_str(title_art)+2 #4

	if menu_width != 0 and beer_panel_w_delta == 0:
		beer_panel_w_delta += max((((screen_width - menu_width) // max_cols) - 2), 0) #4), 0)
		if change_set_menu_width == 0:
			change_set_menu_width = 1
	panel_w += beer_panel_w_delta

	if not beers_init:
		beers_init = True

	while (start_col+panel_w) > (screen_width):
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

	panel.border(ls, rs, ts, bs, tl, tr, bl, br)
	#panel.border()

	inner_text_offset = 4 #5  #3
	row_cnt = 1 #2
	top = title_art[0].strip()
	# pad_cnt = 0
	# while (len(top)+4) < panel_w:
	# 	top = ' ' + top + ' '
	# 	pad_cnt += 1
	pad_cnt = (panel_w - len(top)) / 2

	for line in title_art:
		line = line.strip()
		#startcol = int(pad_cnt*0.75) + (inner_text_offset//3)

		startcol = int(pad_cnt) #+ (inner_text_offset//3)
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
		try:
			panel.addstr(row_cnt, startcol, line, attr)
		except:
			pass
		row_cnt+=1
	row_cnt+=1
	# bar_len = ((panel_w - (inner_text_offset*2)) + 2)
	bar_start = (inner_text_offset // 2)
	bar_len = panel_w - inner_text_offset 

	if DEBUG_BEER:
		log_debug(f'col_title={title}\n\tpanel_w={panel_w}, bar_len={bar_len}, delta={beer_panel_w_delta}' \
			f'\n\tmenu_width={menu_width}, term_width={screen_width}', beer_debug_file)
	panel.addstr(row_cnt, bar_start, '~'*bar_len) #, attr)
	row_cnt+=2 #1

	# inner_text_offset -= 3

	for row, line in enumerate(content):
		row_cnt += 1
		s = str(line).strip()
		if (len(s) > 1) and ((start_row+row+row_cnt) < (start_row+panel_h)):
			if CENTER_MENU_TEXT:
				inner_text_offset = (panel_w - len(s)) // 2
			else:
				inner_text_offset = 4
			panel.addstr(row+row_cnt, inner_text_offset, s, attr)
		row_cnt += (LINE_SPACE-1)


	panel.attrset(curses.color_pair(WHITE))
	return panel_w if title.lower() != 'name' else panel_w+2


def create_heaps_panel(window, start_row, start_col, title, content, max_rows=4, content_color=GREEN, title_art_font=heaps_lbls_font):
	global menu_rows_fit_error, change_set_menu_height, heaps_panel_h_delta, heaps_init #, heaps_fit_err_cnt
	panel = None
	if not HEAPS_LABELS_AS_IMGS:
		title_art_font = 'term'
	title_art = get_art(title_art_font, title)
	title_art_lines = len(title_art)

	screen_height, screen_width = max_dimensions(window)

	panel_h = len(content) + title_art_lines + 3 #4 #5
	
	if menu_height != 0 and heaps_panel_h_delta == 0:
		heaps_panel_h_delta += max(((screen_height - menu_height) // max_rows), 0)  # -5), 0)
		if change_set_menu_height == 0:
			change_set_menu_height = 1
	panel_h += heaps_panel_h_delta

	if not heaps_init:
		heaps_init = True

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

	panel.border(ls, rs, ts, bs, tl, tr, bl, br)
	#panel.border()

	inner_text_offset = 4 #2
	row_cnt = 1 #2

	if HEAPS_LABELS_AS_IMGS:
		"""
		top = title_art[0].strip()
		pad_cnt = 0
		while (len(top)+4) < panel_w:
			top = ' ' + top + ' '
			pad_cnt += 1
		for line in title_art:
			line = line.strip()
			startcol = int(pad_cnt) + (inner_text_offset//3)
			panel.addstr(row_cnt, startcol, line, attr|curses.A_BOLD) #|curses.A_UNDERLINE)
			row_cnt+=1
		"""

		## First draw the label art on the lefthand side of the panel, mid-height
		midrow_start = (panel_h - title_art_lines) // 2
		art_row_cnt = midrow_start
		for line in title_art:
			panel.addstr(art_row_cnt, inner_text_offset, line.strip(), attr)
			art_row_cnt += 1

		longest_line = 0
		for i in range(len(content)):
			if len(str(content[i]).strip()) > longest_line:
				longest_line = len(str(content[i]).strip())

		## Then write out the food menu items on the right, 2 spaces below the panel top
		food_row_cnt = (inner_text_offset // 2) - 1
		for num, item in enumerate(content):
			line = str(content[num]).strip()
			if len(line)>1:
				# if food_row_cnt == inner_text_offset:
				if num == 0:
					line = title.strip() + '  { ' + line + ' }'
				title_end_x = inner_text_offset + len(title_art[0].strip())
				line_start_x = 0
				pad = inner_text_offset

				## For a right-aligned listing:
				if food_alignment == RIGHT_ALIGN:
					pad = len(line) + inner_text_offset
					# right_edge = panel_w + start_col
					line_start_x = panel_w - pad
					# if num == 0:
					# 	line_start_x -= (inner_text_offset * 2)
				
				## For a left-aligned listing:
				elif food_alignment == LEFT_ALIGN:
					# pad = title_end_x
					while (title_end_x + len(line) + pad) >= (panel_w - inner_text_offset):
						pad -= 1
					while (title_end_x + longest_line + pad) <= (panel_w - int(inner_text_offset * 1.5)):
						pad += 1
					line_start_x = title_end_x + pad
				
				## Centered menu item alignment (between title image and panel width)
				elif food_alignment == CENTER_ALIGN: 
					line_start_x = title_end_x + (((panel_w - title_end_x) - len(line)) // 2)

				if num == 0:
					line_start_x = (panel_w - len(line)) // 2

				# if DEBUG_HEAPS:
				# 	log_debug(f'panel_title={title}\n\tpanel_h={panel_h},\tpanel_w={panel_w}' \
				# 		f'\n\tline_start_x={line_start_x},\ttitle_end_x={title_end_x},' \
				# 		f'\tfood_row_cnt={food_row_cnt},\n\tline={line}', food_debug_file)

				try:
					panel.addstr(food_row_cnt, line_start_x, line, attr)
				except:
					menu_rows_fit_error = True
				food_row_cnt += (LINE_SPACE - 1)

		if DEBUG_HEAPS:
			log_debug(f'panel_title={title}\n\tpanel_h={panel_h},\tpanel_w={panel_w}' \
				f'\n\tmenu_height={menu_height},\tterm_height={screen_height}', food_debug_file)

		panel.attrset(curses.color_pair(WHITE))
		return panel_h

	else:
		top = title + '  { ' + str(content[0]).strip() + ' }'
		startcol = ((panel_w - len(top)) // 2)  # + start_col
		panel.addstr(row_cnt, startcol, top, attr|curses.A_UNDERLINE)
		row_cnt+=2

		bar_start = inner_text_offset
		bar_len = panel_w - (inner_text_offset * 2)
		panel.addstr(row_cnt, bar_start, '~'*bar_len)

	if DEBUG_HEAPS:
		log_debug(f'panel_title={title}\n\tpanel_h={panel_h},\tdelta={heaps_panel_h_delta}' \
			f'\n\tmenu_height={menu_height},\tterm_height={screen_height}', food_debug_file)

	# inner_text_offset += 4

	for row, line in enumerate(content):
		# row_cnt += 1  	<-- Will include blank, spacer lines 
		if not HEAPS_LABELS_AS_IMGS and row == 0:
			continue
		s = str(line).strip()
		if (len(s) > 1):
			if ((start_row+row+row_cnt) < (start_row+panel_h)):
				row_cnt += 1
				# if not HEAPS_LABELS_AS_IMGS:
				# 	row_cnt += 1
				if CENTER_MENU_TEXT: # or row == 0:
					inner_text_offset = ((panel_w - len(s)) // 2) - 2
				else:
					inner_text_offset = 12
				if HEAPS_LABELS_AS_IMGS and row == 0:
					panel.addstr(row_cnt, inner_text_offset, '{ '+s+' }', attr|curses.A_UNDERLINE)
				else:
					panel.addstr(row_cnt, inner_text_offset, s, attr)
			else:
				global heaps_lbls_font
				# if heaps_fit_err_cnt < len(alt_heaps_lbl_fonts):
				# 	heaps_lbls_font = alt_heaps_lbl_fonts[heaps_fit_err_cnt]
				# 	heaps_fit_err_cnt += 1
				# else:
				heaps_lbls_font = 'term'
				heaps_init = False
				change_set_menu_height = 1

	panel.attrset(curses.color_pair(WHITE))
	return panel_h

def create_merch_panel(window, start_row, start_col, header_width, title, content, max_cols=2, content_color=GREEN):
	global menu_rows_fit_error
	panel = None 
	screen_height, screen_width = max_dimensions(window)
	panel_h = screen_height - start_row + 1 #3

	panel_w = (header_width // max_cols) #+ 1
	if title.lower() != 'cost':
		panel_w += 1

	try:
		panel = window.derwin(panel_h, panel_w, start_row, start_col)
	except:
		return panel_w 
	if panel is None:
		return panel_w

	attr_list = [
		curses.A_BOLD,
	]
	attr = curses.color_pair(content_color)
	panel.attrset(attr)
	for a in attr_list:
		attr |= a

	panel.border(ls, rs, ts, bs, tl, tr, bl, br)

	row_cnt = 1 #2

	if content:
		for row, line in enumerate(content):
			# row_cnt += 1
			
			s = str(line).strip()
			#ss = str(line).strip()
			if len(s) > 1:
			#if len(ss) > 1:
				row_cnt+=1
				#s_img = get_art('smmono9', ss)
				#for l in s_img:
					#s = l.strip()
				if (start_row+row+row_cnt) < (start_row+panel_h):
					#attr = (curses.A_BOLD | curses.A_UNDERLINE | curses.A_STANDOUT)
					## With contents as plaintext:
					if CENTER_MENU_TEXT:
						inner_text_offset = (panel_w - len(s)) // 2
					else:
						inner_text_offset = 4
					panel.addstr(row_cnt, inner_text_offset, s, attr)
				else:
					menu_rows_fit_error = True
			row_cnt += (LINE_SPACE-1)

	panel.attrset(curses.color_pair(WHITE))

	return panel_w

def draw_merch_header(window, start_row, content=merch_header_text, content_color=GREEN, title_art_font=merch_lbl_font):
	panel = None
	title_art = get_art(title_art_font, content)
	#title_art_lines = len(title_art)
	screen_height, screen_width = max_dimensions(window)
	panel_h = len(title_art) + 4 #3 #2 #title_art_lines + 8 #10 #6 #4
	panel_w = int(len(title_art[1].strip()) * 2) #1.5)  
	if panel_w > screen_width:
		panel_w = screen_width - 8 #4
	#while panel_w % 2 != 0:
	#	panel_w -= 1
	# panel_w = screen_width - (4*start_col) - 1
	#while panel is None:
	#	try:
	start_row = len(logo_img)+1

	start_col = (screen_width - panel_w) // 2
	try:
		panel = window.derwin(panel_h, panel_w, start_row, start_col)
	except:
		start_col = 4
	panel = window.derwin(panel_h, panel_w, start_row, start_col)
	#		panel_h -= 1
	#	return panel_w 
	#if panel is None:
	#	return panel_w

	attr_list = [
		curses.A_BOLD,
	]
	attr = curses.color_pair(content_color)
	panel.attrset(attr)
	for a in attr_list:
		attr |= a

	panel.border(ls, rs, ts, bs, tl, tr, bl, br)

	#top = title_art[1].strip()
	#pad_col = (panel_w - len(top)) // 2
	row_cnt = 2 #1
	for row, line in enumerate(title_art):
		pad_cnt = (panel_w - len(title_art[row].strip())) // 2
		panel.addstr(row_cnt, pad_cnt, line.strip(), attr)
		#row_cnt = 1
	#for line in title_art:
		# panel.addstr(start_row+1+row, pad_col, line.strip(), attr)
		#panel.addstr(start_row+row_cnt, pad_col, line.strip(), attr)
		row_cnt += 1

	panel.attrset(curses.color_pair(WHITE))
	return panel_h, panel_w, start_col


def draw_menu(window, menu):
	global menu_width, menu_height, menu_toprow, change_set_menu_width, change_set_menu_height
	nkeys = len(menu.keys())
	next_y = len(logo_img) 		# Represents height of logo art file
	if LOGO_SCROLL or CENTER_LOGO:
		next_y += 1
	next_x = 3
	offset = 0

	if menu_state == HEAPS:
		for k in menu.keys():
			offset = create_heaps_panel(window, next_y, next_x, k, menu.get(k), nkeys)
			old_next_y = next_y
			next_y += (offset - 1)
			if DEBUG_HEAPS:
				log_debug(f'\tstart_y = {old_next_y},\tend_y = {next_y}\n', food_debug_file)
		if DEBUG_HEAPS:
			log_debug(('='*20) + '\n', food_debug_file)
	elif menu_state == MERCH:
		head_y, head_width, head_start_col = draw_merch_header(window, next_y) #, next_x)
		next_y += head_y
		if LOGO_SCROLL or CENTER_LOGO:
			next_y -= 1
		next_x = head_start_col
		for k in menu.keys():
			offset = create_merch_panel(window, next_y, next_x, head_width, k, menu.get(k), nkeys)
			next_x += (offset - 1)
	else:
		for k in menu.keys():
			offset = create_beers_panel(window, next_y, next_x, k, menu.get(k), nkeys)
			old_next_x = next_x
			next_x += (offset - 1)
			if DEBUG_BEER:
				log_debug(f'\tstart_x = {old_next_x},\tend_x = {next_x}\n', beer_debug_file) 
		if DEBUG_BEER:
			log_debug(('='*20) + '\n', beer_debug_file)

	if (menu_width == 0 or change_set_menu_width == 1) and beers_init:
		menu_width = next_x
		if change_set_menu_width == 1:
			change_set_menu_width = 2
	if (menu_height == 0 or change_set_menu_height == 1) and heaps_init:
		menu_height = next_y
		if change_set_menu_height == 1:
			change_set_menu_height = 2
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

	start_row = 1 if (LOGO_SCROLL or CENTER_LOGO) else 0

	start_column = None #logo_x
	end_column = None #logo_end_x  #start_column + longest_str(image)
	first_col = None  ## THIS IS THE COLUMN INDEX TO BEGIN DRAWING FROM
	last_col = terminal_width  							# Dummy large value to initialize

	if logo_state == LOGO_ON_SCREEN or logo_state == LOGO_WRAP_RIGHT:  ## Use both logo_x & logo_end_x
		for row, line in enumerate(image, start=start_row):
			for column, symbol in enumerate(line, start=logo_x):
				if (column < terminal_width):
					window.addch(row+logo_y, column, symbol, attr)
	# elif logo_state == LOGO_WRAP_RIGHT:
	# elif logo_state == LOGO_OFF_SCREEN:	 ## Reset logo_x & logo_end_x positions
	elif logo_state == LOGO_WRAP_LEFT:  ## Begin drawing from logo_end_x = 0, set logo_x = 0 when logo_end_x == longest_str(img)-1
		if logo_end_x >= (longest_str(image) - 1):
			logo_x = -3 #0
		else:
			for row, line in enumerate(image, start=start_row):			# Start from 1 to leave row space for prompt_str
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
	global logo_img, menu_rows_fit_error, LINE_SPACE, logo_x, logo_end_x, menu_state, ls,rs,ts,bs,tl,tr,bl,br #, menu_state_timestamp
	curses.start_color()
	curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.curs_set(0)
	menu_opts = menu_dict()
	# prompt_len = len(prompt_str)
	toggle_cursor = False
	toggle_char = '_'
	scroll_cnt = 0
	scroll_speed = 7  #5
	logo_img = get_art(logo_font, logo_text)
	logo_len = longest_str(logo_img)
	if CENTER_LOGO:
		logo_x = (max_dimensions(window)[1] - logo_len) // 2
	else:
		logo_x = max_dimensions(window)[1] - logo_len - 3 #4) #10)
	logo_end_x = logo_x + logo_len #longest_str(logo_img)

	ls=curses.ACS_PLUS #LTEE
	rs=curses.ACS_PLUS #RTEE
	ts=curses.ACS_HLINE #curses.ACS_PLMINUS
	bs=curses.ACS_HLINE #'='
	tl=curses.ACS_ULCORNER
	tr=curses.ACS_URCORNER
	bl=curses.ACS_SSBB
	br=curses.ACS_LRCORNER

	if DEBUG_BEER:
		if os.path.exists(beer_debug_file):
			os.system(f'rm {beer_debug_file}')
			beer_dict_out = json.dumps(menu_opts[0], indent=4) 
			if any(menu_opts[1].values()):
				beer_dict_out += '\n' + json.dumps(menu_opts[1], indent=4)
			os.system(f'echo {beer_dict_out} > {beer_debug_file}')
			log_debug(('_'*24)+'\n\n', beer_debug_file)
	if DEBUG_HEAPS:
		if os.path.exists(food_debug_file): 
			os.system(f'rm {food_debug_file}')
			heap_dict_out = json.dumps(menu_opts[2], indent=4)
			os.system(f'echo {heap_dict_out} > {food_debug_file}')
			log_debug(('_'*24)+'\n\n', food_debug_file)
	if DEBUG_MERCH:
		if os.path.exists(merch_debug_file):
			os.system(f'rm {merch_debug_file}')
			merch_dict_out = json.dumps(menu_opts[-1], indent=4)
			os.system(f'echo {merch_dict_out} > {merch_debug_file}')
			log_debug(('_'*24)+'\n\n', merch_debug_file)

	EXCLUSIVE_DEBUG = DEBUG_BEER ^ DEBUG_HEAPS ^ DEBUG_MERCH

	menu_state_timestamp = time.time()

	while True:
		scroll_cnt %= 1000000
		window.erase()
		# window.addstr(2,2,str(scroll_cnt),curses.color_pair(WHITE))
		# window.addstr(2,2,str(max_dimensions(window)[0]),curses.color_pair(WHITE))
		# window.addstr(3,2,str(max_dimensions(window)[1]),curses.color_pair(WHITE))

		if scroll_cnt % scroll_speed != 0:
			draw_logo(window, logo_img, attrs=[curses.A_BOLD]) #, curses.A_UNDERLINE]) #, curses.A_REVERSE]) #, curses.A_BLINK])

		
		if time.time() - menu_state_timestamp >= MENU_CHANGE_PERIOD:
			# if time.time() - menu_state_timestamp >= 60:
			# 	global logo_state
			# 	logo_state = LOGO_WRAP_LEFT
			menu_state_timestamp = time.time()
			menu_state = (menu_state + 1) % len(menu_state_list)
		# state = menu_state_list[menu_state]

		if EXCLUSIVE_DEBUG:
			if DEBUG_BEER:
				if menu_state != BEERS1 or menu_state != BEERS2:
					menu_state = BEERS1
			elif DEBUG_HEAPS:
				menu_state = HEAPS
			else:
				menu_state = MERCH 

		menu = menu_opts[menu_state]
		if not any(menu.values()): # or menu_state == MERCH:
			menu_state_timestamp = time.time()
			menu_state = (menu_state + 1) % len(menu_state_list)
			menu = menu_opts[menu_state]

		draw_menu(window, menu)

		# if menu_rows_fit_error:
		# 	LINE_SPACE -= 1
		# 	menu_rows_fit_error = False

		if LOGO_SCROLL:
			if scroll_cnt % scroll_speed == 0:
				scroll_logo(window, logo_img)


		prompt_dir = 'merch' if menu_state == MERCH else 'food' if menu_state == HEAPS else 'beer'
		window.addstr(0,1,prompt_str.format(prompt_dir))
		if scroll_cnt % 2 == 0:
			toggle_char = '_' if toggle_cursor else ' '
			toggle_cursor = not toggle_cursor
		window.addch(0,1+len(prompt_str.format(prompt_dir)),toggle_char, curses.color_pair(WHITE))

		window.refresh()
		time.sleep(LOOP_SLEEP)
		scroll_cnt += 1


def cleanup(signum, stack):
	# curses.endwin()
	sys.exit(1)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, cleanup)
	curses.wrapper(main)
	# try:
	# 	scr = curses.initscr()
	# except:
	# 	import subprocess
	# 	subprocess.call(['lxterminal', '--command', 'python3', __file__])
	# else:
	# 	main(scr)
