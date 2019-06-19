
import pickle
import sys
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import TransportError
from httplib2 import ServerNotFoundError


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
heaps_ranges = ('heaps!A2:A4', 'heaps!A7:A10', 'heaps!A13:A16', 'heaps!A19:A24')
heaps_ranges_raw = ('A2:A4', 'A7:A10', 'A13:A16', 'A19:A24')
heaps_col_lbls = ('Double Fried Belgian Fries', 'Cheese', 'Meat', 'Heaps Savory New Zealand Pies and Rolls')

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

def log_debug(msg,filename='debug.log'):
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
				beers_col_lbls[i] : parse(read_sheet(sheet, beers_ranges1[i], sid=BEERS_ID))
			}
		)
	for i in range(len(beers_col_lbls)):
		beer_menu2.update(
			{
				beers_col_lbls[i] : parse(read_sheet(sheet, beers_ranges2[i], sid=BEERS_ID))
				
			}
		)
	for i in range(len(heaps_col_lbls)):
		heaps_menu.update(
			{
				heaps_col_lbls[i] : parse(read_sheet(sheet, heaps_ranges[i], sid=HEAPS_ID)) 
				
			}
		)
	return (beer_menu1, beer_menu2, heaps_menu)

def menu_dict_seq(menu_id):
	# Call the Sheets API
	service = validate_service()
	sheet = service.spreadsheets()
	menu = None 
	if menu_id == 0:
		beer_menu1 = dict.fromkeys(beers_col_lbls, [])
		for i in range(len(beers_col_lbls)):
			beer_menu1.update(
				{
					beers_col_lbls[i] :
					read_sheet(sheet, beers_ranges1_raw[i], url=beers_url) # sid=BEERS_ID)
				}
			)
		menu = beer_menu1
	elif menu_id == 1:
		beer_menu2 = dict.fromkeys(beers_col_lbls, [])
		for i in range(len(beers_col_lbls)):
			beer_menu2.update(
				{
					beers_col_lbls[i] :
					read_sheet(sheet, beers_ranges2_raw[i], url=beers_url) # sid=BEERS_ID)
				}
			)
		menu = beer_menu2
	elif menu_id == 2:
		heaps_menu = dict.fromkeys(heaps_col_lbls, [])
		for i in range(len(heaps_col_lbls)):
			heaps_menu.update(
				{
					heaps_col_lbls[i] :
					read_sheet(sheet, heaps_ranges_raw[i], url=heaps_url) # sid=HEAPS_ID)
				}
			)
		menu = heaps_menu
	return menu 



def test_menu_dict():
	print('Begin test:\n')
	menu_opts = menu_dict()
	for item in menu_opts:
		print(item)
		print()

if __name__=='__main__':
	test_menu_dict()
