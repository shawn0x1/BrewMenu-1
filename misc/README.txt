To update all files anytime + install dependencies for first time use (from BrewMenu/):
$ mv updateBrewMenu.sh .. && cd .. && sudo ./updateBrewMenu.sh
^ will automatically run setup.py; some configs (like apt source mirrors) are specific to RPi running Stretch Lite

To run the menu GUI:
$ python3 brewmenu.py

Only necessary files:
- brewmenu.py
- getmenu.py
- images.py
- values.py
- setup.py
- credentials.json
- token.pickle
- fig.img
- menu_example.csv
- updateBrewMenu.sh
________________________________________________________________________________
Objective:
+ Create a Bash-styled beer menu for Halfway Crooks Brewing & Blending
+ Deployment target is to run on Raspberry Pi with output to HDMI
+ Event-specific TUI application example located in the CocktailHour directory

Methods:
+ A Python script will leverage Google APIs for retrieving menu data from a Google Sheets document
+ Various formatting tools & ASCII art utilities will produce an aesthetic rendering of the menu contents
+ The `fbi` utility is great for displaying .png or .jpeg images from the CLI

NOTES:
-- The 'credentials.json' file in this directory is a client config/auth file for Google Sheets API
-- Client ID:       736669249098-genlclcfbf50f9ii73qi4qfmm8s7toen.apps.googleusercontent.com
-- Client Secret:   n9jklMUqkU5nJPiKq1OGtxZZ
-- To install the Google Client Library:
	$ pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
--- ^ alternative install options: https://developers.google.com/api-client-library/python/start/installation
*--- better to use: (worked for me)
	$ sudo easy_install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

***
For client_secret.json, MUST copy client_email (halfwaycrooks@brewmenu.iam.gserviceaccount.com) and share the Google Doc with that email exactly
***

>>> SHAWN WILL NEED TO SET UP HALFWAY CROOKS EMAIL FOR SUPPORT && AUTHORIZATION (I will still need access -- currently tied to my gmail account though, may be alright if I stay on as an admin for tech support)


THOUGHTS (Workinglist):
-- quickstart.py example opens a browser window requesting a Google account sign in...how to circumvent?
---^ This only happens the very first time; authentication creds pickled & saved for all subsequent runs!
-- should the brewmenu program run on startup?

Resources & References:
+ https://developers.google.com/sheets/api/guides/concepts
+ https://developers.google.com/sheets/api/samples/sheet#determine_sheet_id_and_other_properties
+ https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get
+ https://developers.google.com/sheets/api/quickstart/python
+ https://github.com/gsuitedevs/python-samples/blob/master/sheets/snippets/spreadsheet_snippets.py
+ https://developers.google.com/sheets/api/guides/values
+ https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
+ https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
https://developers.google.com/api-client-library/python/auth/installed-app *******
https://developers.google.com/sheets/api/guides/authorizing#APIKey ****
https://developers.google.com/api-client-library/python/auth/api-keys


hostname:           crooks
crooks login:       halfway
passwd:             *******
halfway@crooks:/mnt/usb/brewmenu
/home/halfway/BrewMenu

On RPi:
`sudo dpkg-reconfigure console-setup`
^ allows for adjusting UTF-8 character sets && font size for terminal
