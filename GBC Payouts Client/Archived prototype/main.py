import gspread
from oauth2client.service_account import ServiceAccountCredentials
from booster import Booster
from paid import PaidBooster
import json
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time

if __name__ == "__main__":
    patterns = "*.json"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = False
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

def on_modified(event):
    changed = read_file()

    i = 0
    for key in changed.keys():
        x = changed[key]
        for i in range(len(x)):
            y = x[i]
            paid = PaidBooster(y['Name'], changed[key], y['Amount'], y['Paid'])
            if paid.paid == "TRUE":
                cell = sheet.find(paid.name)
                sheet.update_cell(cell.row, pcol, "TRUE")
    print("Sheet updated successfully!")

my_event_handler.on_modified = on_modified

path = "."
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('payouts_info.json', scope)
client = gspread.authorize(creds)

# Find a sheet by name and open the first tab
# Make sure you use the right name here.
sheet = client.open("Payouts").sheet1

# Set starting points on the sheet
row = 3
col = 3
gcol = 6
pcol = 5
prefcol = 4
data = {}

with open("balance.json", "w") as json_file:
    while row < 20:    
        booster = Booster(sheet.cell(row, col).value, sheet.cell(row, prefcol).value, sheet.cell(row, gcol).value, sheet.cell(row, pcol).value)
        if booster.realm in data:
            data[booster.realm].append({
            'Name' : booster.name,
            'Amount' : booster.amount,
            'Paid' : booster.paid
            })
        else:                       
            data[booster.realm] = []
            data[booster.realm].append({
            'Name' : booster.name,
            'Amount' : booster.amount,
            'Paid' : booster.paid
            })
        row += 1
        time.sleep(1)
    json.dump(data, json_file, indent=4, ensure_ascii=False)
    print("Data written successfully!")

def read_file():
    with open("balance.json", "r") as read_json:
        result = json.load(read_json)
    return result

my_observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()