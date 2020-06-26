# Menu for demonstrating client/server network API

# menu.py
import client
import server
import os
import time
import sys
def main():
    login()
    
def login():
    print("Welcome to the Soap Tech terminal interface!\nPlease enter your login details below.\n")
    username = "soapy_joe"
    password = "washem1"
    print("Enter username : ")
    inp1 = input()
    print("Enter password : ")
    inp2 = input()
    if inp1 == username and inp2 == password:
        print("\nWelcome - Access Granted")
        menu()
    else:
        print("\nIncorrect login details.\nPlease try again.\n")
        login()

def menu():
    print("************MAIN MENU**************")
    time.sleep(1)

    choice = input("""
                      A: Establish server
                      B: Log out

                      Please enter your choice: """)

    if choice == "A" or choice =="a":
        connectDevice()
    elif choice == "B" or choice == "b":
        print("\nThank you for using our product!")
        sys.exit
    else:
        print("You must only select either A or B.\nPlease try again.")
        menu()

def connectDevice():
    os.system('python3 server.py')

main()