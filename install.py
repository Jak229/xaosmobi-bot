import os
from rich import print
from configparser import ConfigParser

conf = ConfigParser()
conf.read("config.ini")

os.system("pip install -r requirements.txt")
os.system("clear||cls")

login = conf["SETTINGS"]["login"]
password = conf["SETTINGS"]["password"]
spc = conf["SETTINGS"]["spaces"]

print("[bold yellow]You use spaces? (1-yes, 0-no)")
spc = input("--> ")

if spc == "0":
    if login and password:
        print("[bold green]Type python3 main.py")
    else:
        print("[bold yellow]Type your name in game.")
        login = input("---> ")

        print("[bold yellow]Type your password.")
        password = input("---> ")
        print("[bold green]Type python3 main.py")


else:
    if login and password:
        print("[bold green]Type python3 main.py")
    else:
        print("[bold yellow]Type your user_id.")
        login = input("---> ")

        print("[bold yellow]Type your password_hash.")
        password = input("---> ")
        print("[bold green]Type python3 main.py")


conf["SETTINGS"]["login"] = login
conf["SETTINGS"]["password"] = password
conf["SETTINGS"]["spaces"] = spc

with open("config.ini", "w") as cnf:
    conf.write(cnf)
