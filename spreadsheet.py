import time
import pygn
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from profanity import profanity
from PyLyrics import *

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/evanj/WMTU/client_secret.json', scope)
client = gspread.authorize(creds)

# pygn info
gracenote_file = open("/home/evanj/WMTU/gracenote.txt", 'r')
clientID = str(gracenote_file.readline()).rstrip('\n')
userID = str(gracenote_file.readline()).rstrip('\n')

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


        # Song info from Columns 1 and 2
        artist = songs[i][0]
        track = songs[i][1]

        # Update genre
        if not songs[i][3]:
            updated = True
            try:
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
            except TypeError:
                sheet.update_cell(i+1, 4, "unknown")

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

        # Update location
        if not songs[i][5]:
            sheet.update_cell(i+1, 6, "not yet added")
            updated = True

        if updated:
            count += 1

# end timing
end = time.time()
print 'Updated ' + str(count) + ' songs'
print 'elapsed time: %.2f s' % (end-start)
