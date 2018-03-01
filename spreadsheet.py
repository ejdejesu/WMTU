import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from profanity import profanity
from PyLyrics import *

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/evanj/python/client_secret.json', scope)
client = gspread.authorize(creds)

# name = input('Enter setlist date to check (MM/DD/YY): ')

# Open Setlist spreadsheet
setlist = client.open("Setlist")

# begin timing
start = time.time()

# Check all worksheets
for s in range(len(setlist.worksheets())):

    # Get current worksheet
    sheet = setlist.get_worksheet(s)

		# print str(sheet.cell(1, 5).value + " - " + sheet.title

    if str(sheet.cell(4, 7).value) == 'FALSE':
        continue

    # Get all tuples from sheet
    songs=sheet.get_all_values()

    # Number of checked songs
    count=0

    print 'Checking setlist ' + sheet.title

    # Check all songs in worksheet
    for i in range(len(songs)-1, 0, -1):

         # Update column 5
        if not str(sheet.cell(i+1, 5).value):
            sheet.update_cell(i+1, 5, "not yet added")

        # Only check if status is not listed
        if str(sheet.cell(i+1, 4).value):
            continue

        artist=songs[i][0]
        track=songs[i][1]
        contains=""

        # Try to find lyrics and profanity level
        try:
            lyrics=PyLyrics.getLyrics(artist, track)
            contains='profane' if profanity.contains_profanity(
                lyrics) else 'clean'
            print 'Song ' + str(i) + ' checked'
        except ValueError:
            contains="unknown"

        # Update column 4 of each song with profanity value
        sheet.update_cell(i+1, 4, contains)
        count=count + 1

    print 'Checked ' + str(count) + ' songs in setlist ' + sheet.title

# end timing
end=time.time()
print 'elapsed time: ' + str(end - start) + ' s'
