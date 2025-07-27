from main_controller1 import MainController
from customtkinter import *


def main():
    desired_storing_format = str(
        input(
            "Would you rather using JSON or Database ?\n1)JSON \n2)Database\npress 1 for json and any key for database\n"
        )
    )
    desired_interface = str(
        input(
            "Would you rather using customtkinter or Terminal ?\n1)gui \n2)Terminal\npress 1 for gui and any key for terminal.\n "
        )
    )
    if desired_storing_format == "1":
        model = "json"
    else:
        model = "db"

    if desired_interface == "1":
        inteface = "gui"
    else:
        inteface = "terminal"

    if inteface == "gui":
        root = CTk()
        main_controller = MainController(model, inteface, root)
        root.mainloop()
    else:
        root = CTk()
        main_controller = MainController(model, inteface, root)


if __name__ == "__main__":
    main()
