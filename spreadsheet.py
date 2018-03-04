import time
import pygn
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from profanity import profanity
from PyLyrics import *

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/pi/setlist/client_secret.json', scope)
client = gspread.authorize(creds)

# pygn info
clientID = '29007503-98DC3B84B17D61D50C67122A6F46BD1E'
userID = '51046582983290877-17F88B114B7ED6E2C1A777FC3777E703'

# Open Setlist spreadsheet
setlist = client.open("Setlist")

# begin timing
start = time.time()

# Number of songs updated
count = 0

# Check all worksheets
for s in range(len(setlist.worksheets())):

    # Get current worksheet
    sheet = setlist.get_worksheet(s)
    if str(sheet.cell(4, 7).value) == 'TRUE':
        continue

    # Get all tuples from sheet
    songs = sheet.get_all_values()

    # Number of checked songs

    print 'Checking setlist ' + sheet.title

    # Check all songs in worksheet
    for i in range(len(songs)-1, 3, -1):

        # If row is empty
        if not songs[i][0]:
            continue

        # Determines if a song's info has been edited
        updated = False

        # Update location
        if not songs[i][5]:
            sheet.update_cell(i+1, 6, "not yet added")
            updated = True

        # Song info from Columns 1 and 2
        artist = songs[i][0]
        track = songs[i][1]

        # Update genre
        if not songs[i][3]:
            updated = True
            metadata = pygn.search(
                clientID=clientID, userID=userID, artist=str(artist), track=str(track))
            genres = metadata['genre']
            output = ""
            # Add all three genres
            for j in range(len(genres)):
                value = str(genres[str(j+1)]['TEXT'])
                output += (value if value != 'Alternative & Punk' else 'Alternative') + \
                    (', ' if j < len(genres)-1 else "")
            sheet.update_cell(i+1, 4, output)

        # Only check if status is not listed
        if not songs[i][4]:
            updated = True

            # Profanity flag
            contains = ""

            # Try to find lyrics and profanity level
            try:
                lyrics = PyLyrics.getLyrics(artist, track)
                contains = 'profane' if profanity.contains_profanity(lyrics) else 'clean'
                print 'Song ' + str(i) + ' updated'
            except ValueError:
                # Lyrics cannot be found
                contains = "unknown"
                print 'ERROR finding lyrics to ' + str(artist) + ' - ' + str(track)

            # Update column 5 of each song with profanity value
            sheet.update_cell(i+1, 5, contains)

        if updated:
            count += 1

# end timing
end = time.time()
print 'Updated ' + str(count) + ' songs'
print 'elapsed time: %.2f s' % (end-start)
