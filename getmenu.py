# Should take in the Google Sheets ID as an argument
# Don't forget to:
#	$ pip3 install --upgrade google-api-python-client
#	$ pip3 install google-auth-oauthlib
#   ....

## Project ID: brewmenu
## Service Account: halfwaycrooks@brewmenu.iam.gserviceaccount.com
## API Key: AIzaSyAdgHKg2486SOH-aFmcf3d9P_H4UwS4Wx0
import pickle
import sys
import os
import values as val
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import TransportError
from httplib2 import ServerNotFoundError

DEFAULT_CSV="menu_example.csv"
SINGLE_REQUEST = False

# SHEET_ID = sys.argv[1:]
# CELL_RANGE = 'A2:D8'

sheet_url = val.sheet_url
start_idx = sheet_url.index('/d/') + 3
end_idx = sheet_url.index('/edit')
SHEET_ID = sheet_url[start_idx:end_idx]
CELL_RANGE = val.sheet_cell_range

col_lbls = val.col_lbls
col_num = len(col_lbls)

# menu = dict.fromkeys(col_lbls, [])
ranges = [val.COL1_RANGE, val.COL2_RANGE, val.COL3_RANGE, val.COL4_RANGE, val.COL5_RANGE]

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] #.readonly']
# API_KEY = 'AIzaSyAdgHKg2486SOH-aFmcf3d9P_H4UwS4Wx0'  # Only for public data, else need OAuth2 credentials

def log_debug(msg,filename='getmenu.debug'):
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
	network = True
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			try:
				creds.refresh(Request())
			except TransportError:
				log_debug('TransportError caught: Failed to establish connection\n-- using local .csv instead')
				network = False
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json',
				 SCOPES)
			creds = flow.run_local_server()
		if network:
			# Save the credentials for the next run
			with open('token.pickle', 'wb') as token:
				pickle.dump(creds, token)


	if network:
		try:
			service = build('sheets', 'v4', credentials=creds) #, developerKey=API_KEY)
		except ServerNotFoundError:
			log_debug('ServerNotFoundError caught: Failed to establish connection\n-- using local .csv instead')
			network = False

	if network:
		# Call the Sheets API
		sheet = service.spreadsheets()

		""" spreadsheets.values Collection JSON Structure:
		{
	  		"range": string,					<-- range of cell covered in A1 format
	  		"majorDimension": enum(Dimension),	<-- ROWS ([[1,2],[3,4]]) or COLUMNS ([[1,3],[2,4]])
	  		"values": 							<-- (ListValue format)
	    		[				<-- This is an array of arrays, the outer array representing all the data
	    			array		<-- and each inner array representing a major dimension.
	    		]				<-- Each item in the inner array corresponds with one cell.
		}
		"""

		if SINGLE_REQUEST:
			result = read_sheet(sheet, CELL_RANGE)

			for i in range(len(col_lbls)):
				i_str = ''
				for v in result[i]:
					i_str += str(v) + ', '
				# os.system('echo "'+i_str+'" >> menu_debug.log')
				menu.update(
					{
						col_lbls[i] :
						result[i]
					}
				)
		else:
			for i in range(len(col_lbls)):
				menu.update(
					{
						col_lbls[i] :
						read_sheet(sheet, ranges[i])
					}
				)

		debug_str = ""
		keys = menu.keys()
		for k in keys:
			debug_str = debug_str + k + ': '
			for v in menu.get(k):
				debug_str = debug_str + str(v) + ' '
			debug_str = debug_str + '\n'
		os.system('echo "'+debug_str+'" >> menu_out.txt')
		# i.e., {"Make" : ["Lower", "Var", "Settings", "Gleaner", ... ], "Type" : [...]}

	else:
		# Load contents of local backup .csv menu file
		# col_lbls = ['Name', 'Type', 'ABV', 'Pour', 'Cost']
		import csv
		f = open(DEFAULT_CSV)
		csv_f = csv.reader(f)
		r = 0
		names=[]
		types=[]
		abvs=[]
		pours=[]
		costs=[]
		hardcodecosts=['Cost','$5','$4','$5','$6','$4','$4','$4','$4','$4','$4','$4','$4','$4','$4','$4']
		for row in csv_f:
			if r>0:
				names.append(row[0])
				types.append(row[1])
				abvs.append(row[2])
				pours.append(row[3])
				# temp = (row[4][1:]).replace('.','')
				# temp = (row[4][1:]).replace('$','')
				# temp = int(temp)
				temp = str(row[4])
				# if temp == 'Cost':
				# 	newcost = temp
				if not any(x.isnumeric() for x in temp):
					newcost = temp
				else:
					if len(temp)==0:
						log_debug("cost value returned null")
					# temp=temp.replace('$','')
					for c in temp:
						if not c.isnumeric():
							temp=temp.replace(c,'')
					newcost = "${:.2f}".format(float(temp))#/100.0)
				# costs.append(row[4])
				costs.append(newcost)
				# costs.append(hardcodecosts[r-1])
			r+=1
		menu.update({col_lbls[0]:names})
		menu.update({col_lbls[1]:types})
		menu.update({col_lbls[2]:abvs})
		menu.update({col_lbls[3]:pours})
		menu.update({col_lbls[4]:costs})
		# menu.update({col_lbls[4]:hardcodecosts})
		# log_debug(menu)
	print(menu)
	return menu
