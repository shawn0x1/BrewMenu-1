import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets']

keyfile_json = 'client_secret.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile_json, scope)

# token = 

gc = gspread.authorize(creds)
# sheet = gc.open('menu_example')
# sheet = gc.open('brewmenu')
sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=0')
# beers_sheet = gc.open('beers')
# beers_url = 'https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=0'
# beers_sheet = gc.open_by_url(beers_url)
# beers_sheet = sheet.worksheet("beers")
beers_sheet = sheet.get_worksheet(0)
# heaps_sheet = gc.open('heaps')
# heaps_url = 'https://docs.google.com/spreadsheets/d/13AHRFbjuJ1F6LEDU5o2949DCyCFtPAxXZgHg2fLH_jc/edit?ts=5c8913ff#gid=1702929798'
# heaps_sheet = gc.open_by_url(heaps_url)
# heaps_sheet = sheet.worksheet("heaps")
heaps_sheet = sheet.get_worksheet(1)

for i in range(5):
	print(beers_sheet.col_values(i+1))
	print()

print(heaps_sheet.col_values(1))
