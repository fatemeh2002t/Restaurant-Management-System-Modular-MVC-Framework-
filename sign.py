from abstract import *
from customtkinter import *
from CTkMessagebox import CTkMessagebox

from abstract import ModelInterface


class Enterance_SIGN_Controller(ControllerInterface):
    def __init__(
        self,
        main_controller,
        interface: sign_in_sign_up_enterance,
    ):
        self.__main_controller = main_controller
        self.__view = interface
        self.__history = []

    def show_view(self, next_view):
        self.__view.pack_forget()  # Hide current view
        self.__history.append(self.__view)
        self.__view = next_view
        self.__view.set_controller(self)

    def go_back(self, event=None):
        self.__view.pack_forget()
        self.__view = self.__history.pop()
        self.__view.set_controller(self)

    def owner_sign_in_choice(self, event=None):
        self.__role = "owner"
        if isinstance(self.__view, Terminal_owner_customer_enterance):
            self.show_view(Terminal_Customer_Owner_Sign_In())
        else:
            self.show_view(GUI_Customer_Owner_Sign_In(self.__view.root))

    def customer_sign_in_choice(self, event=None):
        self.__role = "customer"
        if isinstance(self.__view, Terminal_owner_customer_enterance):
            self.show_view(Terminal_Customer_Owner_Sign_In())
        else:
            self.show_view(GUI_Customer_Owner_Sign_In(self.__view.root))

    def owner_sign_up_choice(self, event=None):
        self.__role = "owner"
        if isinstance(self.__view, Terminal_owner_customer_enterance):
            self.show_view(Terminal_Customer_Owner_Sign_UP())
        else:
            self.show_view(GUI_Customer_Owner_Sign_UP(self.__view.root))

    def customer_sign_up_choice(self, event=None):
        self.__role = "customer"
        if isinstance(self.__view, Terminal_owner_customer_enterance):
            self.show_view(Terminal_Customer_Owner_Sign_UP())
        else:
            self.show_view(GUI_Customer_Owner_Sign_UP(self.__view.root))

    def signing_up(self, event=None):
        self.__main_controller.model_is_needed(1)
        user_name = self.__view.get_user_name()
        password = self.__view.get_password()
        self.__model.create_model(self.__role)
        self.__model[user_name] = password
        valid = self.__model.represent_report()
        self.__view.clear_entires()
        if valid:
            self.__view.successful_operation()
            self.next_mvc()
        else:
            self.__view.wrong_operation()

    def signing_in(self, event=None):
        self.__main_controller.model_is_needed(1)
        user_name = self.__view.get_user_name()
        password = self.__view.get_password()
        self.__model.create_model(self.__role)
        result = self.__model.authentification(user_name, password)
        self.__view.clear_entires()
        if result:
            self.__view.successful_operation()
            self.next_mvc()
        else:
            self.__view.wrong_operation()

    def next_mvc(self):
        if self.__role == "owner":
            self.__view.pack_forget()
            self.__main_controller.next_view(2)
        else:
            self.__view.pack_forget()
            self.__main_controller.next_view(3)

    def get_model(self, model: ModelInterface) -> None:
        self.__model = model


#################################################################################
##################################################################################


class GUI_owner_customer_enterance(sign_in_sign_up_enterance):
    def __init__(self, root: CTk) -> None:
        self.__root = root

    @property
    def root(self):
        return self.__root

    def create_widgets(self):
        self.__frame = CTkFrame(self.__root)
        self.__frame.pack(expand=True, fill="both")

        self.__customer_label = CTkLabel(
            master=self.__frame, text="Customer", font=("Tahoma", 20)
        )
        self.__customer_label.grid(row=0, column=1, padx=10, pady=10)
        self.__owner_label = CTkLabel(
            master=self.__frame, text="Owner", font=("Tahoma", 20)
        )
        self.__owner_label.grid(row=2, column=1, padx=10, pady=10)
        self.__customer_sign_in = CTkButton(
            master=self.__frame, text="Sign In", font=("Tahoma", 20)
        )
        self.__customer_sign_in.grid(row=1, column=0, padx=10, pady=10)
        self.__customer_sign_up = CTkButton(
            master=self.__frame, text="Sign Up", font=("Tahoma", 20)
        )
        self.__customer_sign_up.grid(row=1, column=2, padx=10, pady=10)
        self.__owner_sign_in = CTkButton(
            master=self.__frame, text="Sign In", font=("Tahoma", 20)
        )
        self.__owner_sign_in.grid(row=3, column=0, padx=10, pady=10)
        self.__owner_sign_up = CTkButton(
            master=self.__frame, text="Sign Up", font=("Tahoma", 20)
        )
        self.__owner_sign_up.grid(row=3, column=2, padx=10, pady=10)

    def binding(self):
        print("*******************")
        print(self._controller)
        self.__customer_sign_in.bind(
            "<Button-1>", self._controller.customer_sign_in_choice
        )
        self.__customer_sign_up.bind(
            "<Button-1>", self._controller.customer_sign_up_choice
        )

        self.__owner_sign_in.bind("<Button-1>", self._controller.owner_sign_in_choice)
        self.__owner_sign_up.bind("<Button-1>", self._controller.owner_sign_up_choice)

    # def pack(self):
    #     self.__frame.pack(expand=True, fill="both")

    def pack_forget(self):
        self.__frame.pack_forget()

    def get_user_name(self):
        pass

    def get_password(self):
        pass

    def successful_operation(self):
        pass

    def wrong_operation(self):
        pass

    def clear_entires(self):
        pass


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class Terminal_owner_customer_enterance(sign_in_sign_up_enterance):

    def create_widgets(self):
        print("Welcome\nplease enter a number according to your role and task.\n")
        print(
            "1)Customer Sign Up \n2)Customer Sign In \n3) Owner Sign Up\n4) Owner Sign In\n"
        )
        self.__user_choice = int(input("Please enter a number:"))

    def binding(self):
        self.__cases = {
            1: self._controller.customer_sign_up_choice,
            2: self._controller.customer_sign_in_choice,
            3: self._controller.owner_sign_up_choice,
            4: self._controller.owner_sign_in_choice,
        }
        self.__cases[self.__user_choice]()

    def get_user_name(self):
        pass

    def get_password(self):
        pass

    def successful_operation(self):
        pass

    def wrong_operation(self):
        pass

    def pack_forget(self):
        os.system("cls")

    def clear_entires(self):
        pass


##################################################################################
##################################################################################


class GUI_Customer_Owner_Sign_UP(sign_in_sign_up_enterance):
    def __init__(self, root: CTk):
        self.__root = root

    def create_widgets(self):
        self.__frame = CTkFrame(self.__root)
        self.__frame.pack(expand=True, fill="both")

        self.__username_label = CTkLabel(
            master=self.__frame, text="Username", font=("Tahoma", 20)
        )
        self.__username_label.grid(row=0, column=1, padx=10, pady=10)
        self.__password_label = CTkLabel(
            master=self.__frame, text="Password", font=("Tahoma", 20)
        )
        self.__password_label.grid(row=1, column=1, padx=10, pady=10)
        self.__username_entry = CTkEntry(master=self.__frame)
        self.__username_entry.grid(row=0, column=2, padx=10, pady=10)
        self.__password_entry = CTkEntry(master=self.__frame)
        self.__password_entry.grid(row=1, column=2, padx=10, pady=10)
        self.__register_button = CTkButton(master=self.__frame, text="Register")
        self.__register_button.grid(row=2, column=2, padx=10, pady=10)
        back_arrow = chr(8592)
        self.__back_button = CTkButton(
            master=self.__frame, width=50, height=50, text=back_arrow
        )
        self.__back_button.grid(row=0, column=0, padx=10, pady=10)

    def get_user_name(self):
        return self.__username_entry.get()

    def get_password(self):
        return self.__password_entry.get()

    def binding(self):
        self.__register_button.bind("<Button-1>", self._controller.signing_up)
        self.__back_button.bind("<Button-1>", self._controller.go_back)

    def pack_forget(self):
        self.__frame.pack_forget()

    def pack(self):
        self.__frame.pack(expand=True, fill="both")

    def successful_operation(self):
        CTkMessagebox(
            title="Sign Up Status",
            message="Sign up successful!\nwelcome dear friend",
            icon="check",
            option_1="Thanks",
        )

    def wrong_operation(self):
        CTkMessagebox(
            title="Sign Up Status",
            message="Username already exists.\nTry with different username or password buddy",
            icon="warning",
            option_1="OK",
        )

    def clear_entires(self):
        self.__password_entry.delete(0, END)
        self.__username_entry.delete(0, END)


class Terminal_Customer_Owner_Sign_UP(sign_in_sign_up_enterance):

    def create_widgets(self):
        self.__user_name = str(input("Enter your Desired User_name: \n"))
        self.__Password = str(input("Enter your Desired Password : \n"))

    def binding(self):
        self._controller.signing_up()

    def get_user_name(self):
        return self.__user_name

    def get_password(self):
        return self.__Password

    def pack_forget(self):
        os.system("cls")

    def successful_operation(self):
        print("sign up successful\nWelcome dear friend")

    def wrong_operation(self):
        print("Username already exists.\nTry with different username or password buddy")

    def clear_entires(self):
        pass


###############################################################################################################
#####################################################################################################################
class GUI_Customer_Owner_Sign_In(sign_in_sign_up_enterance):
    def __init__(self, root: CTk):
        self.__root = root

    def create_widgets(self):
        self.__frame = CTkFrame(self.__root)
        self.__frame.pack(expand=True, fill="both")

        self.__username_label = CTkLabel(
            master=self.__frame, text="Username", font=("Tahoma", 20)
        )
        self.__username_label.grid(row=0, column=1, padx=10, pady=10)
        self.__password_label = CTkLabel(
            master=self.__frame, text="Password", font=("Tahoma", 20)
        )
        self.__password_label.grid(row=1, column=1, padx=10, pady=10)
        self.__username_entry = CTkEntry(master=self.__frame)
        self.__username_entry.grid(row=0, column=2, padx=10, pady=10)
        self.__password_entry = CTkEntry(master=self.__frame)
        self.__password_entry.grid(row=1, column=2, padx=10, pady=10)
        self.__register_button = CTkButton(master=self.__frame, text="Enter")
        self.__register_button.grid(row=2, column=2, padx=10, pady=10)
        back_arrow = chr(8592)
        self.__back_button = CTkButton(
            master=self.__frame, width=50, height=50, text=back_arrow
        )
        self.__back_button.grid(row=0, column=0, padx=10, pady=10)

    def binding(self):
        self.__register_button.bind("<Button-1>", self._controller.signing_in)
        self.__back_button.bind("<Button-1>", self._controller.go_back)

    def get_user_name(self):
        return self.__username_entry.get()

    def get_password(self):
        return self.__password_entry.get()

    def pack_forget(self):
        self.__frame.pack_forget()

    def pack(self):
        self.__frame.pack(expand=True, fill="both")

    def successful_operation(self):
        CTkMessagebox(
            title="Sign In Status",
            message="Sign In successful!\nwelcome back dear friend",
            icon="check",
            option_1="Thanks",
        )

    def wrong_operation(self):
        CTkMessagebox(
            title="Sign In Status",
            message="Wrong username or password.\nTry again buddy",
            icon="warning",
            option_1="OK",
        )

    def clear_entires(self):
        self.__password_entry.delete(0, END)
        self.__username_entry.delete(0, END)


class Terminal_Customer_Owner_Sign_In(sign_in_sign_up_enterance):

    def create_widgets(self):
        self.__user_name = str(input("Enter your User_name: \n"))
        self.__Password = str(input("Enter your Password : \n"))

    def binding(self):
        self._controller.signing_in()

    def get_user_name(self):
        return self.__user_name

    def get_password(self):
        return self.__Password

    def pack_forget(self):
        os.system("cls")

    def successful_operation(self):
        print("successful Sign In!\nwelcome back dear friend")

    def wrong_operation(self):
        print("Wrong username or password.\nTry again buddy")
        self.create_widgets()

    def clear_entires(self):
        pass


######################################################
