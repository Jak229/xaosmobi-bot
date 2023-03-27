import os
from rich import print
from bot.bot import Bot
from configparser import ConfigParser
from bot.errors import ItemHasMaxQualityLevel

conf = ConfigParser()
conf.read("config.ini")


def clear():
    os.system("clear||cls")


def menu():
    name = conf["SETTINGS"]["login"]
    password = conf["SETTINGS"]["password"]
    spc = conf["SETTINGS"]["spaces"]

    bot = Bot(name=name, password=password, spaces=True if spc == "1" else False)

    if bot.login():
        print(f"[bold green][{name}] You are logged in to your account")
        input("Press enter to continue")

        while True:
            clear()

            print(
                f"[bold blue]Account: {name}\n"
                "[bold yellow][1] Arena\n"
                "[bold yellow][2] WorkShop\n"
                "[bold yellow][0] Exit"
            )

            var = input(">>> ")

            if not var.isdigit():
                print("[bold red]Enter a number")
                input("Press enter to try againt")
                continue

            if var == "1":
                print("[bold yellow]How many times to go through the arena?")
                var_arn = input(">>> ")

                if not var_arn.isdigit():
                    print("[bold red]Enter a number")
                    input("Press enter to try againt")
                    continue

                bot.arena(var_arn)
                input("End! Press enter")
                continue

            elif var == "2":
                wrk_l = bot.get_link("wrk")
                items = [i.find("table").text for i in bot.get_equipment(wrk_l)]

                for i, item in enumerate(items, start=1):
                    print("[%i] %s\n" % (i, item.strip()))

                num_item = input(">>> ")

                if not num_item.isdigit():
                    print("[bold red]Enter a number")
                    input("Press enter to try againt")
                    continue

                while True:
                    print(
                        f"[bold blue]Account: {name}\n"
                        "[bold yellow][1] Raise the quality\n"
                        "[bold red][2] Enchant\n"
                        "[bold yellow][0] Back\n"
                    )

                    wrks_var = input(">>> ")

                    if not wrks_var.isdigit():
                        print("[bold red]Enter a number")
                        input("Press enter to try againt")
                        continue

                    if wrks_var == "1":
                        print(
                            "[bold yellow]How many times to improve the quality of the item?"
                        )
                        n = input(">>> ")

                        if not n.isdigit():
                            print("[bold red]Enter a number")
                            input("Press enter to try againt")
                            continue

                        try:
                            bot.up_quality(num_item, n)
                            input("End. Press enter")

                        except ItemHasMaxQualityLevel:
                            print("[bold red]This item has max quality level")
                            input("Press enter")
                            continue

                    elif wrks_var == "0":
                        break

                    else:
                        continue

            elif var == "0":
                exit()

    else:
        print("[bold red]Failed to log in to the account")


if __name__ == "__main__":
    menu()
