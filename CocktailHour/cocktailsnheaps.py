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


########## Google Sheets API section #######################
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# LOGO_RANGE = 'A1:B1'
COL1_RANGE = 'A2:A14'
COL2_RANGE = 'B2:B14'
ranges = [COL1_RANGE, COL2_RANGE]
col_lbls = ['Cocktails', 'Heaps']
sheet_url = "https://docs.google.com/spreadsheets/d/10NSm1MrEVvPW8rU-VovIqx5LTTbhriOBcYrcYDcKe6w/edit?ts=5ce61161#gid=0"
start_idx = sheet_url.index('/d/') + 3
end_idx = sheet_url.index('/edit')
SHEET_ID = sheet_url[start_idx:end_idx]

def log_debug(msg,filename='debug.log'):
	print(msg)
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
lblfonts = ['future', 'emboss', 'bubble', 'digital', 'mini', 'small', 'smscript', 'smslant']
lbls_font = lblfonts[0]
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
		if split_text[0] == '-':
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
# border_chars = [
# 	curses.ACS_LTEE,
# 	curses.ACS_RTEE,
# 	curses.ACS_HLINE,
# 	curses.ACS_HLINE,
# 	curses.ACS_ULCORNER,
# 	curses.ACS_URCORNER,
# 	curses.ACS_SSBB,
# 	curses.ACS_LRCORNER
# 	]
menu_width = 0
menu_toprow = 0
logo_x = 0       # <-- formerly 'col_offset = terminal_width() - 1'
logo_y = 0
logo_img = None

def max_dimensions(window):
	height, width = window.getmaxyx()
	return height - 2, width

def divided_col_width(window, ncols):
	return max_dimensions(window)[1] // ncols

def create_panel(window, start_row, start_col, title, content, max_cols=5, content_color=GREEN, title_art_font=lbls_font):
	global menu_rows_fit_error
	panel = None
	title_art = get_art(title_art_font, title)
	title_art_lines = len(title_art)
	screen_height = max_dimensions(window)[0]
	panel_h = screen_height - start_row + 1 #3
	while (start_row+panel_h) > (screen_height + 2):
		panel_h-=1
	panel_w = longest_str(content)
	if panel_w > divided_col_width(window, max_cols):
		panel_w = divided_col_width(window, max_cols)

	# if not FIT_SCREEN:
	# 	trim = max_dimensions(window)[1] // 20
	# 	panel_w -= int(trim)

	panel = window.subwin(panel_h, panel_w, start_row, start_col)  # or can use window.derwin()
	if panel is None:
		return panel_w

	attribute_list = [
		curses.A_BOLD,
		# curses.A_UNDERLINE,
		# curses.A_STANDOUT,
		# curses.A_BLINK,
		# curses.A_HORIZONTAL,
		# curses.A_LEFT,
		# curses.A_LOW,
		# curses.A_VERTICAL,
	]
	attr = curses.color_pair(content_color)
	for a in attribute_list:
		attr |= a
	panel.attrset(attr)

	# ls=border_chars[0]
	# rs=border_chars[1]
	# ts=border_chars[2]
	# bs=border_chars[3]
	# tl=border_chars[4]
	# tr=border_chars[5]
	# bl=border_chars[6]
	# br=border_chars[7]
	# panel.border(ls, rs, ts, bs, tl, tr, bl, br)
	panel.border()

	inner_text_offset = 3
	row_cnt = 1
	top = title_art[0].strip()
	buff_cnt = 0
	while (len(top)+4) < panel_w:
		top = ' ' + top + ' '
		buff_cnt += 1

	for line in title_art:
		line = line.strip()
		startcol = int(buff_cnt*0.75) + inner_text_offset
		# if title.lower() == 'type' and line == title_art[0].strip():
		#     startcol -= 1
		panel.addstr(row_cnt, startcol, line)
		row_cnt+=1

	panel.addstr(row_cnt, inner_text_offset, '-'*(panel_w-inner_text_offset*2))
	#row_cnt+=1

	item_cnt = 0
	for row, line in enumerate(content):
		for s in line:
			if s != title:
				row_cnt+=1
				# if title.lower() == 'cost':
				#     s = '${:.2f}'.format(float(s))
				# elif title.lower() == 'abv':
				#     s = '{:.1f}%'.format(float(s) * 100)
				if start_row+row+row_cnt < start_row+panel_h:
					panel.addstr(row+row_cnt, inner_text_offset, str(s).strip())
				else:
					menu_rows_fit_error = True
				row_cnt += (LINE_SPACE-1)
  
	panel.attrset(curses.color_pair(WHITE))
	return panel_w

def draw_menu(window, menu):
	global menu_width, menu_toprow
	ncols = len(menu.keys())
	next_col_y = len(logo_img) + 1 		# Represents height of logo art file
	next_col_x = 3 
	# if not FIT_SCREEN:
	#     if menu_width > 0:
	#         next_col_x = int((max_dimensions(window)[1] - menu_width) / 2)
	offset = 0
	for k in col_lbls:
		offset = create_panel(window, next_col_y, next_col_x, k, menu.get(k), ncols)
		next_col_x += (offset - 1)
	if menu_width == 0:
		menu_width = next_col_x
	if menu_toprow == 0:
		menu_toprow = next_col_y

def draw_logo(window, image, attrs=None):
	terminal_width = max_dimensions(window)[1]
	start_column = terminal_width - logo_x
	end_column = start_column + longest_str(image)
	if start_column < 0:
		start_column = 0
	attr = curses.color_pair(GREEN)
	if attrs is not None:
		for a in attrs:
			attr |= a
	window.attrset(attr)
	for row, line in enumerate(image, start=1):
		# overflow = False
		for column, symbol in enumerate(line, start=start_column):
			if (column < terminal_width):
				window.addch(row+logo_y, column%terminal_width, symbol)

	window.attrset(curses.color_pair(WHITE))

def scroll_logo(window, image):
	global logo_x
	max_x = max_dimensions(window)[1] - 1
	new_x = (logo_x-3) if (logo_x-3) > 0 else max_x
	logo_x = new_x

def main(window):
	global logo_img, menu_rows_fit_error, LINE_SPACE
	curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.curs_set(0)
	menu = menu_dict()
	prompt_len = len(prompt_str)
	toggle_cursor = False
	toggle_char = '_'
	scroll_cnt = 0
	scroll_speed = 5
	logo_img = get_art(logo_font, logo_text)

	while True:
		scroll_cnt %= 100
		window.erase()
		window.addstr(0,1,prompt_str)
		if scroll_cnt % 2 == 0:
			toggle_char = '_' if toggle_cursor else ' '
			toggle_cursor = not toggle_cursor
		window.addch(0,1+prompt_len,toggle_char, curses.color_pair(WHITE))# | curses.A_BLINK)

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
