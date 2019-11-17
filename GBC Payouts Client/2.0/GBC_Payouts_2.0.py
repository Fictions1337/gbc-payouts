# +----------------------------------------------+
# | Gallywix Boosting Community Payout Tool v2.0 |
# +----------------------------------------------+

# <-------------------IMPORTS START------------------->
import re
# Pyperclip library for inserting data into clipboard
import pyperclip
# Time library so we can use sleep
import time
# Keyboard library for listening for specific keys
import keyboard
# Colorama for looks of our output in the console
from colorama import init
from colorama import Fore, Back, Style
# Rquests allows us to send HTTP requests to the Web Service
import requests
# <--------------------IMPORTS END-------------------->

# Initializing Colorama modules
init()

print(Style.BRIGHT + "F1 - move forward | skip people | confirm payout" + Style.RESET_ALL)
print(Style.BRIGHT + "F2 - get mail note message | get gold amount" + Style.RESET_ALL)
print(Style.BRIGHT + "F5 - go backwards to previous player" + Style.RESET_ALL)
    
# Setting up global variables
URL = 'http://159.69.154.56:9006'
path = 'payout_log.txt'
first = True
f1_pressed = False
f2_pressed = False
f5_pressed = False
paid_check = False
i = 0
confirmation = input("Do you want to start payouts on a specific realm? y/n ")

# Verifying user input, fetching data from the Database,
# printing out information to the console

def escape_ansi(line):
    ansiescape = re.compile(r'(?:\x1B[@-]|[\x80-\x9F])[0-?][ -/][@-~]')
    return ansiescape.sub('', line)

def print_twice(args):
    line = args
    text = escape_ansi(line)
    print(args)
    with open(path,"a") as f:  # appends to file and closes it when finished
       f.write(text)

def realm_pick():
    global data
    global total
    response = requests.get(URL + '/get/pref_realm')
    all_realms = response.json()
    list_of3 = []
    pairs = []
    counter = 0
    realms = {}
    r_count = 0
    for e in range(len(all_realms)):
        if len(pairs) < 3:
            pairs.append(all_realms[e].pop())
        else:
            list_of3.append(pairs)
            pairs = []
    for b in list_of3:
        for z in b:
            realms[r_count] = z.replace('/', '-')
            r_count += 1
    elem_count = 0
    for key, value in realms.items():
        print (key, value)
    pref_realm = input('Enter the Realm ID of the realm you want to start on: ')
    try:
        if int(pref_realm) in realms:
            response = requests.get(URL + '/get/realm/' + realms[int(pref_realm)])
            data = response.json()
            total = len(data)
            if not data:
                print(Fore.RED + "You have specified a wrong realm ID. Please try again." + Style.RESET_ALL)
                realm_pick()
            else:
                print(Fore.MAGENTA + "Total number of players on " + pref_realm + " for payout is " + Style.BRIGHT + str(total) + Style.RESET_ALL)
                print("Use " + Style.BRIGHT + "F1" + Style.RESET_ALL + " to proceed!")
                return (data,total)
        else:
            print(Fore.RED + "You have specified an invalid Realm ID! Please try again." + Style.RESET_ALL)
            realm_pick()
    except:
        print(Fore.RED + "You have specified an invalid Realm ID! Please try again." + Style.RESET_ALL)
        realm_pick()

if confirmation == "y" or confirmation == "yes" or confirmation == "Y" or confirmation == "YES":
    realm_pick()
else:
    response = requests.get(URL + '/get/all')
    data = response.json()
    total = len(data)
    print(Fore.MAGENTA + "Total number of players for payout is " + Style.BRIGHT + str(total) + Style.RESET_ALL)
    print("Use " + Style.BRIGHT + "F1" + Style.RESET_ALL + " to proceed!")

# Starting main loop
while True:
    # F1 - move forward row by row in the database
    # F1 - check if someone is paid out and update the database setting paid=TRUE
    if keyboard.is_pressed("F1") and not f1_pressed:
        f1_pressed = True
        if paid_check:
            requests.put(URL + '/update/' + str(member_id))
            print_twice(Fore.GREEN + Style.BRIGHT + "Payment successful" + Fore.RESET + Style.RESET_ALL + " for " + Style.BRIGHT + name + Style.RESET_ALL + " with balance " + Style.BRIGHT +  str(amount) + Style.RESET_ALL)
            paid_check = False
        elif i > 0:
            print_twice(Fore.RED + Style.BRIGHT + "Skipped payout" +  Fore.RESET + Style.RESET_ALL + " for " + Style.BRIGHT + name + Style.RESET_ALL + " with balance " + Style.BRIGHT +  str(amount) + Style.RESET_ALL)
        
        if i < total and i > -1:
            member_id = data[i]['id']
            name = data[i]['name']
            paid = data[i]['paid']
            realm = data[i]['pref_realm']
            amount = data[i]['balance']
            i += 1
            pyperclip.copy(name)
            print_twice(Fore.YELLOW + Style.BRIGHT + "Pending payout" +  Fore.RESET + Style.RESET_ALL + " for " + Style.BRIGHT + name + Style.RESET_ALL + " with balance " + Style.BRIGHT +  str(amount) + Style.RESET_ALL)
        else:
            print(Style.BRIGHT + Fore.GREEN + "YOU HAVE FINISHED PAYING OUT " + realm + "!\n" + Style.RESET_ALL)
            continue_check = input("Pick a new realm? y/n ")
            if continue_check == "y" or continue_check == "yes" or continue_check == "Y" or continue_check == "YES":
                realm_pick()
                i = 0
            else:
                break
    elif not keyboard.is_pressed("F1") and f1_pressed:
        f1_pressed = False
       
    # F2 - On first press inserts mail note text in clipboard
    # F2 - On second press inserts gold amount for member in clipboard              
    if keyboard.is_pressed("F2") and not f2_pressed:
        f2_pressed = True
        if first:
            pyperclip.copy("Gallywix Boosting Community payout")
            first = False
        elif not first:
            pyperclip.copy(amount)
            first = True
            paid_check = True
    elif not keyboard.is_pressed("F2") and f2_pressed:
        f2_pressed = False
    
    # F5 - goes back to previous row (member)
    if keyboard.is_pressed("F5") and not f5_pressed:
        f5_pressed = True
        i -= 1             
        print_twice(Fore.LIGHTBLUE_EX + Style.BRIGHT + "You went backwards. Click F1 to continue!" + Fore.RESET + Style.RESET_ALL)
    elif not keyboard.is_pressed("F5") and f5_pressed:
        f5_pressed = False
    