from abstract import *
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from abstract import ModelInterface
from reportlab.pdfgen import canvas
from random import randint
from os import system
from datetime import datetime
from reportlab.pdfgen import canvas


class customer_controller(ControllerInterface):
    def __init__(
        self,
        main_controller,
        interface: MainInterface,
    ):
        self.__main_controller = main_controller
        self.__view = interface
        self.__history = []
        self.__first_view = interface

    def __show_view(self, next_view: MainInterface):
        self.__view.pack_forget()  # Hiding current view
        self.__history.append(self.__view)
        self.__view = next_view
        if isinstance(self.__view, gui_payment) or isinstance(
            self.__view, terminal_payment
        ):
            self.__view.get_info(
                self.__total_price, self.__offer_amount, self.__final_price
            )
        self.__view.set_controller(self)

    def go_back(self, event=None):
        self.__view.pack_forget()
        self.__view = self.__history.pop()
        # print(self.__view,"**********")
        self.__view.set_controller(self)

    def show_menu(self, event=None):
        self.__main_controller.model_is_needed(2)
        food_data = self.__model.get_food_data()
        self.__view.display_report(food_data, "Restaurant Menu")

    def goto_pay(self, event=None):
        self.__orders = self.__view.get_orders()
        self.__order_type = self.__view.get_order_type()
        self.__reservation_date = self.__view.get_reservation_date()
        self.__reservation_table = self.__view.get_reservation_table()
        self.__main_controller.model_is_needed(2)

        self.__total_price = 0
        for food_name, quantity in self.__orders.items():

            price = self.__model.get_food_price(food_name)

            self.__total_price = self.__total_price + int(price) * quantity

        self.__main_controller.model_is_needed(1)
        number_of_order = self.__model.get_order_summary()
        self.__offer_amount = float(number_of_order) * 0.005
        self.__final_price = (1 - self.__offer_amount) * self.__total_price

        if isinstance(self.__view, gui_get_customer_order):
            self.__show_view(gui_payment(self.__view.root))
        else:
            self.__show_view(terminal_payment())

    def process_payment(self, event=None):
        cart_number = self.__view.get_cart_number()
        cvv2 = self.__view.get_cvv2()
        customer_random = self.__view.get_random_input()
        if (
            len(cart_number) == 12
            and len(cvv2) == 4
            and customer_random == self.__view.random_numbers()
        ):
            self.__main_controller.model_is_needed(1)
            for food_name, quantity in self.__orders.items():

                self.__model.add_order(
                    self.__order_type, self.__reservation_date, food_name, quantity
                )

            if self.__order_type == "reservation":

                self.__model.update_reservation(
                    self.__reservation_date, self.__reservation_table
                )

                for food_name, quantity in self.__orders.items():
                    self.__reservation_date = datetime.strptime(
                        self.__reservation_date, "%Y-%m-%d %H:%M:%S"
                    ).strftime("%Y-%m-%d")

                    self.__model.add_reservation_order(
                        self.__reservation_date, food_name, quantity
                    )

            if self.__order_type == "takeout":

                self.__main_controller.model_is_needed(2)  # food model
                ingredients = self.__model.get_ingredients_for_food(food_name)
                for ingredient_name, amount in ingredients.items():

                    total_amount = amount * quantity
                    print("*********", ingredient_name, total_amount, "*************")
                    self.__main_controller.model_is_needed(3)  # Product Model
                    self.__model.update_product_quantity(ingredient_name, total_amount)

            if isinstance(self.__view, gui_payment):
                self.__show_view(payment_success_view(self.__view.root))
            else:
                self.__show_view(terminal_success_view())
        else:

            self.__view.failure()

    def factor_pdf(self, event=None):
        pdf_file_name = "order_receipt.pdf"

        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)

        c = canvas.Canvas(pdf_file_name)
        c.setFont("Helvetica", 12)

        c.drawString(50, 800, "Order Receipt")
        c.drawString(50, 780, f"Order Type: {self.__order_type}")
        if self.__order_type == "reservation":
            c.drawString(50, 760, f"Reservation Date: {self.__reservation_date}")
            c.drawString(50, 740, f"Reservation Table: {self.__reservation_table}")

        y = 720
        for food_name, quantity in self.__orders.items():
            c.drawString(50, y, f"Food Name: {food_name}")
            c.drawString(200, y, f"Quantity: {quantity}")
            y -= 20

        y -= 20
        c.drawString(50, y, f"Total Price: {self.__total_price:.2f} toman")
        y -= 20
        c.drawString(50, y, f"Offer Amount: {self.__offer_amount * 100:.2f}%")
        y -= 20
        c.drawString(50, y, f"Final Price: {self.__final_price:.2f} toman")
        y -= 20
        c.drawString(50, y, "thanks for your shopping")

        c.save()

    def next_mvc(self) -> None:
        pass

    def get_model(self, model: ModelInterface) -> None:
        self.__model = model


###############################################################################################
class gui_get_customer_order(MainInterface):
    def __init__(self, root: CTk) -> None:
        self.__root = root

    @property
    def root(self):
        return self.__root

    def create_widgets(self):
        self.__frame = CTkFrame(self.__root)
        self.__frame.pack(expand=True, fill="both")
        self.__show_menu_button = CTkButton(
            self.__frame, text="Show Menu", font=("Tahoma", 20)
        )
        self.__show_menu_button.grid(row=0, column=0, padx=10, pady=10)
        # Orders frame
        self.__orders_frame = CTkFrame(self.__frame)
        self.__orders_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        self.__orders_entries = []

        self.__add_food = CTkButton(
            self.__frame,
            text="Add Food",
            font=("Tahoma", 20),
            command=self.__add_part_entry,
        )
        self.__add_food.grid(row=2, column=0, padx=10, pady=10)

        self.__order_type = StringVar(value="takeout")
        self.__takeout_radio = CTkRadioButton(
            self.__frame, text="Takeout", variable=self.__order_type, value="takeout"
        )
        self.__takeout_radio.grid(row=3, column=1, padx=10, pady=10)

        self.__reservation_radio = CTkRadioButton(
            self.__frame,
            text="Reserve Table",
            variable=self.__order_type,
            value="reservation",
        )
        self.__reservation_radio.grid(row=3, column=2, padx=10, pady=10)

        self.__reservation_date_label = CTkLabel(
            self.__frame, text="Reservation Date (if applicable):"
        )
        self.__reservation_date_label.grid(row=4, column=1, padx=10, pady=10)
        self.__reservation_date_entry = CTkEntry(self.__frame)
        self.__reservation_date_entry.grid(row=4, column=2, padx=10, pady=10)

        self.__reservation_table_label = CTkLabel(
            self.__frame, text="Reservation Table (1-30) (if applicable):"
        )
        self.__reservation_table_label.grid(row=5, column=1, padx=10, pady=10)
        self.__reservation_table_entry = CTkEntry(self.__frame)
        self.__reservation_table_entry.grid(row=5, column=2, padx=10, pady=10)

        self.__goto_pay = CTkButton(
            self.__frame, text="Go to Payment Page", font=("Tahoma", 20)
        )
        self.__goto_pay.grid(row=3, column=0, padx=30, pady=10)

    def __add_part_entry(self):
        frame = CTkFrame(self.__orders_frame)
        frame.pack(fill="x", pady=5)

        label_food_name = CTkLabel(frame, text="Food Name")
        label_food_name.pack(side="left", padx=10)

        entry_food_name = CTkEntry(frame)
        entry_food_name.pack(side="left", padx=10)

        label_food_number = CTkLabel(frame, text="Number")
        label_food_number.pack(side="left", padx=10)

        entry_food_number = CTkEntry(frame)
        entry_food_number.pack(side="left", padx=10)

        self.__orders_entries.append((entry_food_name, entry_food_number))

    def binding(self):
        self.__show_menu_button.bind("<Button-1>", self._controller.show_menu)
        self.__goto_pay.bind("<Button-1>", self._controller.goto_pay)

    def display_report(self, data: dict, title: str):
        report_window = CTkToplevel(self.__root)
        report_window.title(title)

        text = CTkTextbox(report_window)
        text.pack(expand=True, fill="both")
        report_content = ""
        for food_name, details in data.items():
            report_content += f"Food: {food_name}\n"
            report_content += f"  Price: {details['price']}\n"
            report_content += "  Parts:\n"
            for part_name, part_details in details["parts"].items():
                report_content += (
                    f"    Part: {part_name} - Quantity: {part_details['quantity']}\n"
                )
            report_content += "\n"

        text.insert("1.0", report_content)
        text.configure(state="disabled")

    def get_orders(self):
        orders = {}
        for entry_food_name, entry_food_number in self.__orders_entries:
            food_name = entry_food_name.get()
            food_number = int(entry_food_number.get())
            if food_name in orders:
                orders[food_name] += food_number
            else:
                orders[food_name] = food_number
        return orders

    def get_order_type(self):
        return self.__order_type.get()

    def get_reservation_date(self):
        # print(self.__order_type.get(),"********************")
        if self.__order_type.get() == "takeout":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.__reservation_date_entry.get()

    def get_reservation_table(self):
        return self.__reservation_table_entry.get()

    def pack_forget(self):
        self.__frame.pack_forget()


class terminal_get_customer_oreder(MainInterface):
    def create_widgets(self):
        print("Welcome dear customer. Press any key to see menu...")
        input()
        self._controller.show_menu()
        while True:
            self.__orders = self.__getting_orders()
            self.__order_type = self.__getting_order_type()

            if self.__order_type == "reservation":
                self.__reservation_date = self.__getting_reservation_date()
                self.__reservation_table = self.__getting_reservation_table()
            else:
                self.__reservation_date = ""
                self.__reservation_table = ""

            choice = input(
                "If you want to edit your order, press 1. If you want to go to the payment page, press 2: "
            )
            if choice == "2":
                print("Proceeding to payment...")
                break

    def binding(self):
        self._controller.goto_pay()

    def pack_forget(self):
        import os

        os.system("cls")

    def display_report(self, data: dict, title: str):
        print(f"{title}\n")
        for food_name, details in data.items():
            print(f"Food: {food_name}")
            print(f"  Price: {details['price']}")
            print("  Parts:")
            for part_name, part_details in details["parts"].items():
                print(f"    Part: {part_name} - Quantity: {part_details['quantity']}")
            print("\n")

    def __getting_orders(self):
        orders = {}
        while True:
            food_name = input("Enter food name (or 'done' to finish): ")
            if food_name.lower() == "done":
                break
            try:
                food_number = int(input("Enter quantity: "))
                if food_name in orders:
                    orders[food_name] += food_number
                else:
                    orders[food_name] = food_number
            except ValueError:
                print("Invalid input, please enter a valid number.")
        return orders

    def __getting_order_type(self):
        while True:
            order_type = input("Order type (takeout/reservation): ").lower()
            if order_type in ["takeout", "reservation"]:
                return order_type
            print("Invalid input, please enter 'takeout' or 'reservation'.")

    def __getting_reservation_date(self):
        return input("Enter reservation date (if applicable): ")

    def __getting_reservation_table(self):
        return input("Enter reservation table (1-30) (if applicable): ")

    def get_orders(self):
        return self.__orders

    def get_order_type(self):
        return self.__order_type

    def get_reservation_date(self):
        return self.__reservation_date if self.__reservation_date else None

    def get_reservation_table(self):
        return self.__reservation_table if self.__reservation_table else None


class gui_payment(MainInterface):
    def __init__(self, root: CTk):
        self.__root = root
        self.__random_numbers = [randint(0, 9) for _ in range(5)]

    @property
    def root(self):
        return self.__root

    def random_numbers(self):
        str_lst = [str(i) for i in self.__random_numbers]
        concatenated_str = "".join(str_lst)
        reslt = [int(concatenated_str)]
        #    print(reslt,"***")
        return reslt

    def create_widgets(self):
        self.__frame = CTkFrame(self.__root)
        self.__frame.pack(expand=True, fill="both")

        self.__cart_num_label = CTkLabel(self.__frame, text="Cart Number")
        self.__cart_num_label.grid(row=0, column=1, padx=10, pady=10)

        self.__cart_num_entry = CTkEntry(self.__frame)
        self.__cart_num_entry.grid(row=0, column=2, padx=10, pady=10)

        self.__cart_cvv2_label = CTkLabel(self.__frame, text="CVV2")
        self.__cart_cvv2_label.grid(row=1, column=1, padx=10, pady=10)

        self.__cart_cvv2_entry = CTkEntry(self.__frame)
        self.__cart_cvv2_entry.grid(row=1, column=2, padx=10, pady=10)

        self.__random_label = CTkLabel(
            self.__frame, text=f"Enter this number: {self.__random_numbers}"
        )
        self.__random_label.grid(row=2, column=1, padx=10, pady=10)

        self.__random_entry = CTkEntry(self.__frame)
        self.__random_entry.grid(row=2, column=2, padx=10, pady=10)

        self.__total_label = CTkLabel(
            self.__frame, text=f"Total Price:{self.__total_price:.2f} toman"
        )
        self.__total_label.grid(row=3, column=1, pady=10, padx=10)

        self.__offer_label = CTkLabel(
            self.__frame, text=f"Offer Amount: {self.__offer * 100:.2f}%"
        )
        self.__offer_label.grid(row=4, column=1, pady=10, padx=10)

        self.__final_label = CTkLabel(
            self.__frame, text=f"Final Price: {self.__final_price:.2f} toman"
        )
        self.__final_label.grid(row=5, column=1, pady=10, padx=30)

        self.__pay_BUTTON = CTkButton(self.__frame, text="Pay")
        self.__pay_BUTTON.grid(row=6, column=2, padx=10, pady=10)

        back_arrow = chr(8592)
        self.__back_button = CTkButton(
            master=self.__frame, width=50, height=50, text=back_arrow
        )
        self.__back_button.grid(row=0, column=0, padx=0, pady=0)

    def get_info(self, total_price: float, offer: float, final_price: float):
        self.__total_price = total_price
        self.__offer = offer
        self.__final_price = final_price

    def binding(self) -> None:
        self.__back_button.bind("<Button-1>", self._controller.go_back)
        self.__pay_BUTTON.bind("<Button-1>", self._controller.process_payment)

    def pack_forget(self):
        self.__frame.pack_forget()

    def get_cart_number(self):
        return self.__cart_num_entry.get()

    def get_cvv2(self):
        return self.__cart_cvv2_entry.get()

    def get_random_input(self):
        return list(map(int, self.__random_entry.get().split()))

    def failure(self):
        CTkMessagebox(
            title="payment Status",
            message="Wrong cart_number or cvv2 or entered random number.\nTry again buddy",
            icon="warning",
            option_1="OK",
        )


class terminal_payment(MainInterface):
    def __init__(self):
        self.__random_numbers = [randint(0, 9) for _ in range(5)]

    def random_numbers(self):
        str_lst = [str(i) for i in self.__random_numbers]
        concatenated_str = "".join(str_lst)
        reslt = [int(concatenated_str)]
        return reslt

    def create_widgets(self):
        print(f"Total Price: {self.__total_price:.2f} toman")
        print(f"Offer Amount: {self.__offer * 100:.2f}%")
        print(f"Final Price: {self.__final_price:.2f} toman")

        while True:
            print("Enter the following payment details:")
            self.__cart_number = input("Cart Number (12 digits): ")
            self.__cvv2 = input("CVV2 (4 digits): ")
            print(f"Enter this number: {self.__random_numbers}")
            self.__random_input = input("Enter the number: ")
            print(
                "Is every thing ok\nif you want to finalize payment press on 1\nif you want to go back to order page press on 2\nif you want to edit above info press on any key rather than 1 or 2?\n"
            )
            choice = input("enter:")
            if choice == "1":
                break
            elif choice == "2":
                self._controller.go_back()

    def binding(self) -> None:
        self._controller.process_payment()

    def get_info(self, total_price: float, offer: float, final_price: float):
        self.__total_price = total_price
        self.__offer = offer
        self.__final_price = final_price

    def get_cart_number(self):
        return self.__cart_number

    def get_cvv2(self):
        return self.__cvv2

    def get_random_input(self):
        return list(map(int, self.__random_input.split()))

    def failure(self):
        print("Wrong cart number, CVV2, or entered random number. Try again, buddy.")

    def pack_forget(self):
        system("cls")


################################################################################
class payment_success_view(MainInterface):
    def __init__(self, root: CTk):
        self.__root = root

    @property
    def root(self):
        return self.__root

    def create_widgets(self):
        self.__frame = CTkFrame(self.__root)
        self.__frame.pack(expand=True, fill="both")

        self.__success_label = CTkLabel(self.__frame, text="Payment Successful!")
        self.__success_label.grid(row=0, column=1, pady=40, padx=40)

        self.__download_button = CTkButton(self.__frame, text="Download Receipt")
        self.__download_button.grid(row=2, column=1, padx=40, pady=40)

    def binding(self) -> None:
        self.__download_button.bind("<Button-1>", self._controller.factor_pdf)

    def pack_forget(self):
        self.__frame.pack_forget()


class terminal_success_view(MainInterface):
    def create_widgets(self) -> None:
        print("Payment was sucessful")
        print("if you want to get factor , press on any key ")
        choice = str(input())

    def binding(self) -> None:
        self._controller.factor_pdf()
