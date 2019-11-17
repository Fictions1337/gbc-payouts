# +----------------------------------------------+
# | Gallywix Boosting Community Payout Tool v1.0 |
# +----------------------------------------------+

# <-------------------IMPORTS START------------------->
# MySQL library to execute queries from and to Database
import pymysql
# SSH Tunnel that we use to connect to SQL Server
import sshtunnel
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

# SSH Tunnel global settings
sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

# Opening a SSH connection with the host
with sshtunnel.SSHTunnelForwarder(
    ('159.69.159.113'),
    ssh_username='root', ssh_password='bogipogi',
    remote_bind_address=('localhost', 3306)
) as tunnel:
    # Opening a SQL Server connection through the SSH Tunnel
    connection = pymysql.connect(
        user='root', password='bogipogi',
        host='127.0.0.1', port=tunnel.local_bind_port,
        database='cias',
        autocommit=True
    )
    # Checking connection status
    if (connection):
        print(Fore.CYAN + "Connection to Database established!" + Fore.RESET)
        print(Style.BRIGHT + "F1 - move forward | skip people | confirm payout" + Style.RESET_ALL)
        print(Style.BRIGHT + "F2 - get mail note message | get gold amount" + Style.RESET_ALL)
        print(Style.BRIGHT + "F5 - go backwards 1 to previous player" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Error: Connection to Database failed!" + Fore.RESET)
    with connection:
        # Setting up global variables
        cur = connection.cursor()
        row_count = 1
        first = True
        f1_pressed = False
        f2_pressed = False
        f5_pressed = False
        paid_check = False
        pref_realm_check = False
        member_id = (0,)
        i = 0
        paid_value = ("TRUE",)
        confirmation = input("Do you want to start payouts on a specific realm? y/n ")
        
        # Verifying user input, fetching data from the Database,
        # printing out information to the console
        if confirmation == "y" or confirmation == "yes" or confirmation == "Y" or confirmation == "YES":
            cur.execute("SELECT DISTINCT pref_realm FROM balance2")
            for y in range(100):
                time.sleep(0.03)
                print('Loading Database [%d%%]\r'%y, end="")
            all_realms = cur.fetchall()
            big_list = []
            for element in all_realms:
                big_list.append(element[0])
            list_of_threes = []
            pairs = []
            while len(big_list) > 0:
                if len(pairs) < 3:
                    pairs.append(big_list.pop())
                else:
                    list_of_threes.append(pairs)
                    pairs = []
            biggest_element = max(len(item) for element in list_of_threes for item in element) + 4
            for each_row in list_of_threes:
                print("".join(item.ljust(biggest_element) for item in each_row))
            pref_realm = (input('Enter the name of the realm you want to start on: '))
            pref_realm_check = True
            total = cur.execute("SELECT * FROM balance2 WHERE pref_realm=%s", (pref_realm))
            print(pref_realm)
            print(Fore.MAGENTA + "Total number of players on " + pref_realm + " for payout is " + Style.BRIGHT + str(total) + Style.RESET_ALL)
            print("Use " + Style.BRIGHT + "F1" + Style.RESET_ALL + " to proceed!")
        else:
            main_load = cur.execute("SELECT * FROM balance2")
            for y in range(100):
                time.sleep(0.03)
                print('Loading Database [%d%%]\r'%y, end="")
            print(Fore.MAGENTA + "Total number of players for payout is " + Style.BRIGHT + str(main_load) + Style.RESET_ALL)
            print("Use " + Style.BRIGHT + "F1" + Style.RESET_ALL + " to proceed!")
            
        # Starting main loop
        while True:
            # F1 - move forward row by row in the database
            # F1 - check if someone is paid out and update the database setting paid=TRUE
            if keyboard.is_pressed("F1") and not f1_pressed:
                f1_pressed = True
                if paid_check:
                    cur.execute("UPDATE balance2 SET paid=%s WHERE id=%s", (paid_value, member_id))
                    print(Fore.GREEN + Style.BRIGHT + "Payment successful" + Fore.RESET + Style.RESET_ALL + " for " + Style.BRIGHT + name + Style.RESET_ALL + " with balance " + Style.BRIGHT +  amount + Style.RESET_ALL)
                    paid_check = False
                    if pref_realm_check:
                        cur.execute("SELECT * FROM balance2 WHERE pref_realm=%s", (pref_realm))
                    if not pref_realm_check:
                        cur.execute("SELECT * FROM balance2")
                    x = 0
                    while x < i:
                        cur.fetchmany(row_count)
                        x += 1
                elif i > 0:                    
                    print(Fore.RED + Style.BRIGHT + "Skipped payout" +  Fore.RESET + Style.RESET_ALL + " for " + Style.BRIGHT + name + Style.RESET_ALL + " with balance " + Style.BRIGHT +  amount + Style.RESET_ALL)
                
                row = cur.fetchmany(row_count)
                i += 1
                for item in row:
                    member_id = item[0]
                    name = item[1]
                    paid = item[3]
                    amount = item[4]
                    pyperclip.copy(name)
                    print(Fore.YELLOW + Style.BRIGHT + "Pending payout" +  Fore.RESET + Style.RESET_ALL + " for " + Style.BRIGHT + name + Style.RESET_ALL + " with balance " + Style.BRIGHT +  amount + Style.RESET_ALL)
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
                if pref_realm_check:
                    cur.execute("SELECT * FROM balance2 WHERE pref_realm=%s", (pref_realm))
                if not pref_realm_check:
                    cur.execute("SELECT * FROM balance2")
                i -= 2
                x = 0
                while x < i:
                    cur.fetchmany(row_count)
                    x += 1                
                print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "You went backwards. Click F1 to continue!" + Fore.RESET + Style.RESET_ALL)
            elif not keyboard.is_pressed("F5") and f5_pressed:
                f5_pressed = False
    # Closing SQL connection to the server
    connection.close()
    