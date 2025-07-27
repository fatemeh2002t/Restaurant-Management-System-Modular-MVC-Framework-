from abstract import *
from sqlite3 import *
import json
from datetime import date, timedelta, datetime
from decorators import *


@singleton
class DATA_BASE_model(customer_owner_model):
    def __init__(self) -> None:
        self.__customer_id = None

    def create_model(self, role: str):
        self.__role = role
        self.__user_table_name = f"{self.__role}_user_pass"
        self.__conn = connect(f"{self.__role}_username_password_database.db")
        self.__cur = self.__conn.cursor()
        self.__cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.__user_table_name} (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
            """
        )
        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_type TEXT,
                reservation_date TEXT,
                food_name TEXT,
                quantity INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customer_user_pass(id)
            )
            """
        )
        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS OrderSummary (
                customer_id INTEGER PRIMARY KEY,
                order_count INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customer_user_pass(id)
            )
            """
        )

        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER ,
                reservation_date TEXT,
                reservation_table INTEGER,
                FOREIGN KEY (customer_id) REFERENCES customer_user_pass(id)
            )
            """
        )

        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS reservation_orders (
                date TEXT,
                food_name TEXT,
                quantity INTEGER,
                PRIMARY KEY (date, food_name)
            )
            """
        )

        self.__conn.commit()

    def __setitem__(self, username: str, password: str) -> None:
        self.__cur.execute(
            f"SELECT 1 FROM {self.__user_table_name} WHERE username = ?", (username,)
        )
        self.__valid = self.__cur.fetchone() is None

        if self.__valid:
            self.__cur.execute(
                f"INSERT INTO {self.__user_table_name} (username, password) VALUES (?, ?)",
                (username, password),
            )
            self.__conn.commit()

            self.__customer_id = self.__cur.lastrowid
            # print("previousid")
            # print(self.__customer_id)
            # print("***********")

            # Insert new customer_id into OrderSummary with initial order_count as 0
            if self.__role == "customer":
                self.__cur.execute(
                    "INSERT INTO OrderSummary (customer_id, order_count) VALUES (?, ?)",
                    (self.__customer_id, 0),
                )
                self.__conn.commit()

    def represent_report(self) -> bool:
        return self.__valid

    def authentification(self, username: str, password: str) -> bool:
        self.__cur.execute(
            f"SELECT id, password FROM {self.__user_table_name} WHERE username = ?",
            (username,),
        )
        result = self.__cur.fetchone()
        if result is None or password != result[1]:
            return False
        else:
            self.__customer_id = result[0]
        return True

    def add_order(self, order_type, reservation_date, food_name, quantity):

        self.__cur.execute(
            "DELETE FROM Orders WHERE customer_id = ? AND reservation_date < ?",
            (self.__customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        self.__cur.execute(
            "INSERT INTO Orders (customer_id, order_type, reservation_date, food_name, quantity) VALUES (?, ?, ?, ?, ?)",
            (self.__customer_id, order_type, reservation_date, food_name, quantity),
        )

        self.__cur.execute(
            "INSERT OR REPLACE INTO OrderSummary (customer_id, order_count) VALUES (?, COALESCE((SELECT order_count FROM OrderSummary WHERE customer_id = ?) + ?, ?))",
            (self.__customer_id, self.__customer_id, quantity, quantity),
        )

        self.__conn.commit()

        # self.__cur.execute("SELECT customer_id, order_type, reservation_date, food_name, quantity FROM Orders")
        # result = self.__cur.fetchall()
        # print(result,"***************")

    def update_reservation(self, reservation_date, reservation_table):
        # reservation_date_str = reservation_date.strftime("%Y-%m-%d %H:%M:%S")

        self.__cur.execute(
            "DELETE FROM Reservations WHERE customer_id = ? AND reservation_date < ?",
            (self.__customer_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

        self.__cur.execute(
            "INSERT INTO Reservations (customer_id, reservation_date, reservation_table) VALUES (?, ?, ?)",
            (self.__customer_id, reservation_date, reservation_table),
        )
        self.__conn.commit()

    def get_order_summary(self):
        # print("lastid")
        # print(self.__customer_id)
        self.__cur.execute(
            "SELECT order_count FROM OrderSummary WHERE customer_id = ?",
            (self.__customer_id,),
        )
        result = self.__cur.fetchone()
        return result[0] if result else 0

    def add_reservation_order(self, date, food_name, quantity):
        self.__cur.execute(
            """
            INSERT INTO reservation_orders (date, food_name, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(date, food_name) DO UPDATE SET
            quantity = quantity + excluded.quantity
            """,
            (date, food_name, quantity),
        )
        self.__conn.commit()

    def report_customers(self) -> dict:
        self.__cur.execute("SELECT customer_id, order_count FROM OrderSummary")
        self.__conn.commit()
        result = self.__cur.fetchall()
        return {row[0]: row[1] for row in result}

    def report_reservation_info(self) -> list:
        self.__conn = connect("customer_username_password_database.db")
        self.__cur = self.__conn.cursor()
        self.__cur.execute(
            "SELECT customer_id, reservation_date, reservation_table FROM Reservations"
        )
        result = self.__cur.fetchall()
        return [
            {
                "customer_id": row[0],
                "reservation_date": row[1],
                "reservation_table": row[2],
            }
            for row in result
        ]

    def report_reserved_orders(self) -> dict:
        self.__conn = connect("customer_username_password_database.db")
        self.__cur = self.__conn.cursor()
        self.__cur.execute("SELECT date, food_name, quantity FROM reservation_orders")
        result = self.__cur.fetchall()
        reserved_orders = {}
        for row in result:
            if row[0] not in reserved_orders:
                reserved_orders[row[0]] = {}

            reserved_orders[row[0]][row[1]] = row[2]
        return reserved_orders

    def report_all_orders_info(self) -> list:
        self.__conn = connect("customer_username_password_database.db")
        self.__cur = self.__conn.cursor()
        self.__conn = connect("customer_username_password_database.db")
        self.__cur = self.__conn.cursor()
        self.__cur.execute(
            "SELECT customer_id, order_type, reservation_date, food_name, quantity FROM Orders"
        )
        result = self.__cur.fetchall()
        return [
            {
                "customer_id": row[0],
                "order_type": row[1],
                "reservation_date": row[2],
                "food_name": row[3],
                "quantity": row[4],
            }
            for row in result
        ]


@singleton
class JSON_model(customer_owner_model):
    def __init__(self) -> None:
        self.__Orders = []
        self.__OrderSummary = {}
        self.__Reservations = []
        self.__ReservationOrders = {}
        self.__customer_user_pass = {}
        self.__customer_id = None
        self.__role = ""
        # self.__user_owner_id_counter = 1

    def create_model(self, role: str) -> None:
        self.__role = role
        self.__load_json_files()

    def __load_json_files(self) -> None:
        self.__Orders = self.__load_json_file("customers_Orders.json", [])
        self.__OrderSummary = self.__load_json_file("customers_OrderSummary.json", {})
        self.__Reservations = self.__load_json_file("customers_Reservations.json", [])
        self.__ReservationOrders = self.__load_json_file(
            "customers_ReservationOrders.json", {}
        )
        self.__customer_user_pass = self.__load_json_file(
            f"{self.__role}_username_pass.json", {}
        )

    def __load_json_file(self, filename: str, default):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return default

    def __save_json_file(self, filename: str, data) -> None:
        with open(filename, "w") as file:
            json.dump(data, file)

    def __save_orders(self) -> None:
        self.__save_json_file("customers_Orders.json", self.__Orders)

    def __save_order_summary(self) -> None:
        self.__save_json_file("customers_OrderSummary.json", self.__OrderSummary)

    def __save_reservations(self) -> None:
        self.__save_json_file("customers_Reservations.json", self.__Reservations)

    def __save_reservation_orders(self) -> None:
        self.__save_json_file(
            "customers_ReservationOrders.json", self.__ReservationOrders
        )

    def __save_user_owner_pass(self) -> None:
        self.__save_json_file(
            f"{self.__role}_username_pass.json", self.__customer_user_pass
        )

    def __setitem__(self, username: str, password: str) -> None:
        prior_valid = self.__customer_user_pass.get(username, None)
        self.__valid = prior_valid is None

        if self.__valid:
            if self.__customer_user_pass:
                self.__user_owner_id_counter = (
                    max(
                        [
                            self.__customer_user_pass[user]["id"]
                            for user in self.__customer_user_pass
                        ]
                    )
                    + 1
                )
            else:
                self.__user_owner_id_counter = 1  # Start from 1 if no users exist

            self.__customer_user_pass[username] = {
                "password": password,
                "id": self.__user_owner_id_counter,
            }

            self.__OrderSummary[self.__user_owner_id_counter] = 0

            self.__customer_id = self.__user_owner_id_counter
            # print("********",self.__customer_id)
            self.__save_user_owner_pass()

    def represent_report(self) -> bool:
        return self.__valid

    def authentification(self, username: str, password: str) -> bool:
        user = self.__customer_user_pass.get(username)
        if user and user.get("password") == password:
            self.__customer_id = user.get("id")
            # print("***************",self.__customer_id)
            return True
        return False

    def add_order(
        self, order_type: str, reservation_date: str, food_name: str, quantity: int
    ) -> None:
        # Remove past orders based on reservation_date
        self.__Orders = [
            order
            for order in self.__Orders
            if order["reservation_date"] >= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            or order["customer_id"] != self.__customer_id
        ]

        self.__Orders.append(
            {
                "customer_id": self.__customer_id,
                "order_type": order_type,
                "reservation_date": reservation_date,
                "food_name": food_name,
                "quantity": quantity,
            }
        )

        self.__save_orders()

        # Update OrderSummary
        # print(self.__OrderSummary)
        print(self.__customer_id)
        if str(self.__customer_id) in self.__OrderSummary.keys():
            # print("*******")
            self.__OrderSummary[str(self.__customer_id)] += quantity
        else:
            self.__OrderSummary[self.__customer_id] = quantity
        self.__save_order_summary()

    def update_reservation(self, reservation_date: str, reservation_table: int) -> None:
        # self.__delete_past_reservations(self.__customer_id, reservation_date)
        self.__Reservations = [
            r
            for r in self.__Reservations
            if not (
                r["reservation_date"] < datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                and r["customer_id"] == self.__customer_id
            )
        ]
        self.__Reservations.append(
            {
                "customer_id": self.__customer_id,
                "reservation_date": reservation_date,
                "reservation_table": reservation_table,
            }
        )
        self.__save_reservations()

    def get_order_summary(self) -> int:
        # print("*************",self.__customer_id)
        return self.__OrderSummary.get(str(self.__customer_id), 0)

    def add_reservation_order(self, date, food_name, quantity):
        if date not in self.__ReservationOrders:
            self.__ReservationOrders[date] = {}

        if food_name in self.__ReservationOrders[date]:
            self.__ReservationOrders[date][food_name] += quantity
        else:
            self.__ReservationOrders[date][food_name] = quantity

        self.__save_reservation_orders()

    def report_customers(self) -> dict:
        return self.__OrderSummary

    def report_reservation_info(self) -> list:
        return self.__Reservations

    def report_reserved_orders(self) -> dict:
        return self.__ReservationOrders

    def report_all_orders_info(self) -> list:
        return self.__Orders


########################################################################################


class DB_FoodModel(ModelInterface):
    def __init__(self) -> None:
        self.create_model()

    def create_model(self):
        self.__conn = connect("restaurant.db")
        self.__cur = self.__conn.cursor()
        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Food (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
            """
        )
        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_id INTEGER,
                part_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (food_id) REFERENCES Food (id)
            )
            """
        )
        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER,
                ingredient_name TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (part_id) REFERENCES Parts (id)
            )
            """
        )

        self.__conn.commit()

    def add_food(self, name, price):
        try:
            self.__cur.execute(
                "INSERT INTO Food (name, price) VALUES (?, ?)", (name, price)
            )
            self.__food_id = self.__cur.lastrowid
            self.__valid1 = True
        except:
            self.__valid1 = False

    def add_part(self, part_name: str, quantity):
        try:
            self.__cur.execute(
                "INSERT INTO Parts (food_id, part_name, quantity) VALUES (?, ?, ?)",
                (self.__food_id, part_name, quantity),
            )
            self.__conn.commit()
            self.__valid2 = True
        except:
            self.__valid2 = False

    def add_ingredient(self, part_name: str, ingredient_name: str, quantity: float):
        self.__valid1 = True
        try:
            self.__cur.execute("SELECT id FROM Parts WHERE part_name=?", (part_name,))
            part_id = self.__cur.fetchone()[0]
            self.__cur.execute(
                "INSERT INTO Ingredients (part_id, ingredient_name, amount) VALUES (?, ?, ?)",
                (part_id, ingredient_name, quantity),
            )
            self.__conn.commit()
            self.__valid2 = True
            # print(self.__valid2)
        except:
            # self.__conn.rollback()
            self.__valid2 = False

    def represent_report(self) -> bool:
        return self.__valid1 and self.__valid2

    def get_food_data(self) -> dict:
        food_data = {}
        self.__cur.execute("SELECT id, name, price FROM Food")
        foods = self.__cur.fetchall()  # foods is list of tuples
        for food in foods:
            food_id, food_name, food_price = food
            food_data[food_name] = {"price": food_price, "parts": {}}
            self.__cur.execute(
                "SELECT id, part_name, quantity FROM Parts WHERE food_id=?", (food_id,)
            )
            parts = self.__cur.fetchall()
            for part in parts:
                part_id, part_name, part_quantity = part
                food_data[food_name]["parts"][part_name] = {"quantity": part_quantity}
        return food_data

    def get_food_price(self, food_name: str) -> float:
        self.__cur.execute("SELECT price FROM Food WHERE name=?", (food_name,))
        result = self.__cur.fetchone()
        return result[0] if result else 0.0

    def get_ingredients_for_food(self, food_name):
        self.__cur.execute("SELECT id FROM Food WHERE name=?", (food_name,))
        food_id = self.__cur.fetchone()[0]

        self.__cur.execute("SELECT id, quantity FROM Parts WHERE food_id=?", (food_id,))
        parts = self.__cur.fetchall()

        ingredients = {}
        for part_id, part_quantity in parts:
            self.__cur.execute(
                "SELECT ingredient_name, amount FROM Ingredients WHERE part_id=?",
                (part_id,),
            )
            part_ingredients = self.__cur.fetchall()
            for ingredient_name, amount in part_ingredients:
                if ingredient_name in ingredients:
                    ingredients[ingredient_name] += amount * part_quantity
                else:
                    ingredients[ingredient_name] = amount * part_quantity

        return ingredients


class JSON_FoodModel(ModelInterface):
    def __init__(self):
        self.create_model()
        self.__ingredient = {}

    def create_model(self) -> None:
        try:
            with open("foods.json", "r") as file:
                self.__food_content = json.load(file)
        except:
            with open("foods.json", "w") as file:
                self.__food_content = {}
        try:
            with open("parts.json", "r") as file:
                self.__parts_content = json.load(file)
        except:
            with open("parts.json", "w") as file:
                self.__parts_content = {}
        try:
            with open("ingredients.json", "r") as file:
                self.__ingredient_content = json.load(file)
        except:
            with open("ingredients.json", "w") as file:
                self.__ingredient_content = {}

    def __saving_changes(self) -> None:
        with open("foods.json", "w") as file:
            json.dump(self.__food_content, file)
        with open("parts.json", "w") as file:
            json.dump(self.__parts_content, file)
        with open("ingredients.json", "w") as file:
            json.dump(self.__ingredient_content, file)

    def add_food(self, food: str, price):
        self.__food = food
        self.__parts = {}
        try:
            self.__food_content[food] = price
            self.__saving_changes()
            self.__valid1 = True
        except:
            self.__valid1 = False

    def add_part(self, part_name, quantity):
        try:
            self.__parts[part_name] = quantity
            self.__parts_content[self.__food] = self.__parts
            self.__saving_changes()
            self.__valid2 = True
        except:
            self.__valid2 = False

    def add_ingredient(self, part_name, ingredient_name, ingredient_amount):
        self.__valid1 = True
        try:
            self.__ingredient[ingredient_name] = ingredient_amount
            self.__ingredient_content[part_name] = self.__ingredient
            self.__saving_changes()
            self.__valid2 = True
        except:
            self.__valid1 = False

    def represent_report(self) -> bool:
        return self.__valid1 and self.__valid2

    def get_food_data(self):
        food_data = {}
        for food_name, food_price in self.__food_content.items():
            food_data[food_name] = {"price": food_price, "parts": {}}
            if food_name in self.__parts_content:
                for part_name, part_quantity in self.__parts_content[food_name].items():
                    food_data[food_name]["parts"][part_name] = {
                        "quantity": part_quantity
                    }

        return food_data

    def get_food_price(self, food_name: str) -> float:
        return self.__food_content.get(food_name, 0.0)

    def get_ingredients_for_food(self, food_name):
        # food_id = self.__food_content[food_name]
        parts = self.__parts_content[food_name]

        ingredients = {}
        for part_name, part_quantity in parts.items():
            part_ingredients = self.__ingredient_content[part_name]
            for ingredient_name, amount in part_ingredients.items():
                if ingredient_name in ingredients:
                    ingredients[ingredient_name] += float(amount) * float(part_quantity)
                else:
                    ingredients[ingredient_name] = float(amount) * float(part_quantity)

        return ingredients


#######################################################################################


class DB_ProductModel(ModelInterface):
    def __init__(self) -> None:
        self.create_model()

    def create_model(self):
        self.__conn = connect("products.db")
        self.__cur = self.__conn.cursor()
        self.__cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                number REAL NOT NULL,
                interest REAL NOT NULL,
                entry_date TEXT NOT NULL,
                expiration_date TEXT NOT NULL
            )
            """
        )
        self.__conn.commit()

    def add_product(
        self,
        name: str,
        price: float,
        number: int,
        interest: float,
        entry_date: str,
        expiration_date: str,
    ):
        try:
            self.__cur.execute(
                "INSERT INTO Product (name, price,number, interest, entry_date, expiration_date) VALUES (?, ?,?, ?, ?, ?)",
                (name, price, number, interest, entry_date, expiration_date),
            )
            self.__conn.commit()
            self.__valid = True
        except:
            self.__valid = False

    def represent_report(self) -> bool:
        return self.__valid

    def get_all_products(self):
        self.__cur.execute("SELECT * FROM Product")
        data = self.__returning_in_dict_form(self.__cur.fetchall())
        return data

    def get_expired_products(self):
        current_date = date.today().strftime("%Y-%m-%d")
        self.__cur.execute(
            "SELECT * FROM Product WHERE expiration_date < ?", (current_date,)
        )
        data = self.__returning_in_dict_form(self.__cur.fetchall())
        return data

    def get_nearly_expired_products(self):
        current_date = date.today()
        future_date = current_date + timedelta(days=7)
        self.__cur.execute(
            "SELECT * FROM Product WHERE expiration_date BETWEEN ? AND ?",
            (current_date.strftime("%Y-%m-%d"), future_date.strftime("%Y-%m-%d")),
        )
        data = self.__returning_in_dict_form(self.__cur.fetchall())
        return data

    def __returning_in_dict_form(self, data: list) -> dict:
        temp_dict = {}
        for item in data:
            temp_dict[item[1]] = {
                "price": item[2],
                "number": item[3],
                "interest": item[4],
                "entry_date": item[5],
                "expiration_date": item[6],
            }
        return temp_dict

    def update_product_quantity(self, ingredient_name, amount):
        self.__cur.execute(
            "SELECT number FROM Product WHERE name=?", (ingredient_name,)
        )
        current_quantity = self.__cur.fetchone()[0]
        new_quantity = current_quantity - amount
        self.__cur.execute(
            "UPDATE Product SET number=? WHERE name=?",
            (new_quantity, ingredient_name),
        )
        self.__conn.commit()


class JSON_ProductModel(ModelInterface):
    def __init__(self):
        self.create_model()

    def create_model(self) -> None:
        try:
            with open("products.json", "r") as file:
                self.__product_content = json.load(file)
        except:
            with open("products.json", "w") as file:
                self.__product_content = {}

    def __saving_changes(self) -> None:
        with open("products.json", "w") as file:
            json.dump(self.__product_content, file)

    def add_product(
        self,
        name: str,
        price: float,
        number: int,
        interest: float,
        entry_date: str,
        expiration_date: str,
    ):
        # print(number)
        # print(price)
        try:
            self.__product_content[name] = {
                "price": price,
                "number": number,
                "interest": interest,
                "entry_date": entry_date,
                "expiration_date": expiration_date,
            }
            print(self.__product_content)
            self.__saving_changes()
            self.__valid = True
        except:
            self.__valid = False

    def represent_report(self) -> bool:
        return self.__valid

    def get_all_products(self):
        return self.__product_content

    def get_expired_products(self):
        current_date = date.today().strftime("%Y-%m-%d")
        expired_products = {}
        for name, details in self.__product_content.items():
            if details["expiration_date"] < current_date:
                expired_products[name] = details
        return expired_products

    def get_nearly_expired_products(self):
        current_date = date.today()
        future_date = (current_date + timedelta(days=7)).strftime("%Y-%m-%d")
        current_date = current_date.strftime("%Y-%m-%d")
        nearly_expired_products = {}
        for name, details in self.__product_content.items():
            if (current_date < details["expiration_date"]) and (
                details["expiration_date"] < future_date
            ):
                nearly_expired_products[name] = details
        return nearly_expired_products

    def update_product_quantity(self, name: str, amount: int):

        if name in self.__product_content:
            current_quantity = self.__product_content[name]["number"]
            new_quantity = float(current_quantity) - float(amount)
            if new_quantity < 0:
                raise ValueError("Insufficient quantity available")
            self.__product_content[name]["number"] = new_quantity
            self.__saving_changes()

        else:
            raise ValueError(f"Product '{name}' not found")
