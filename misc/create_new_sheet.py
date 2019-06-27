''' To use, see: https://github.com/gsuitedevs/python-samples/blob/master/sheets/snippets/spreadsheet_snippets.py '''

spreadsheet = {
    'properties': {
        'title': title
    },
    'fields': 'title'
}


spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))