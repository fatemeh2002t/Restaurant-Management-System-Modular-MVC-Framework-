import json
from customtkinter import *
from importlib import import_module


class MainController:
    def __init__(self, desired_model: str, desired_interface: str, root: CTk):
        self.__desired_model = desired_model
        self.__desired_interface = desired_interface
        self.__status = 1
        self.__root = root
        self.__load_json()
        self.__update_view()

    def __load_json(self):
        try:
            with open("sequence_container.json", "r") as file:
                self.__data = json.load(file)
        except FileNotFoundError:
            self.__data = {"view_container": [], "model_container": []}
            self.__save_json()

    def __save_json(self):
        with open("sequence_container.json", "w") as file:
            json.dump(self.__data, file, indent=4)

    def next_view(self, status: int):
        self.__status = status
        self.__update_view()

    def __update_view(self):
        view = next(
            (v for v in self.__data["view_container"] if v["id"] == self.__status), None
        )
        if view:
            controller_class = view["controller"]
            gui_interface_class = view["gui_interface"]
            terminal_interface_class = view["terminal_interface"]
            module_name = view["module_name"]

            interface = self.__get_interface_instance(
                gui_interface_class, terminal_interface_class, module_name
            )
            self.__controller = self.__get_controller_instance(
                controller_class, interface, module_name
            )
            interface.set_controller(self.__controller)
        else:
            print(f"No registered view found for status: {self.__status}")

    def __get_model_instance(self, model_json_class, model_db_class):
        module = import_module("models")
        if self.__desired_model == "json":
            return getattr(module, model_json_class)()
        else:
            return getattr(module, model_db_class)()

    def __get_interface_instance(
        self, gui_interface_class, terminal_interface_class, module_name
    ):
        module = import_module(module_name)
        if self.__desired_interface == "gui":
            return getattr(module, gui_interface_class)(self.__root)
        else:
            return getattr(module, terminal_interface_class)()

    def __get_controller_instance(self, controller_class, interface, module_name):
        module = import_module(module_name)
        return getattr(module, controller_class)(self, interface)

    def register_model(self, db_model: str, json_model: str):
        self.__data["model_container"].append(
            {
                "id": len(self.__data["model_container"]) + 1,
                "model_db": db_model,
                "model_json": json_model,
            }
        )
        self.__save_json()

    def register_view(
        self,
        controller: str,
        gui_interface: str,
        terminal_interface: str,
        module_name: str,
    ):
        self.__data["view_container"].append(
            {
                "id": len(self.__data["view_container"]) + 1,
                "controller": controller,
                "gui_interface": gui_interface,
                "terminal_interface": terminal_interface,
                "module_name": module_name,
            }
        )
        self.__save_json()

    def add_new_view(
        self,
        controller: str,
        gui_interface: str,
        terminal_interface: str,
        position: int,
        module_name: str,
    ):
        temp_id_offset = 100
        for view in self.__data["view_container"]:
            if view["id"] >= position:
                view["id"] += temp_id_offset

        self.__data["view_container"].append(
            {
                "id": position,
                "controller": controller,
                "gui_interface": gui_interface,
                "terminal_interface": terminal_interface,
                "module_name": module_name,
            }
        )

        for view in self.__data["view_container"]:
            if view["id"] >= position + temp_id_offset:
                view["id"] -= temp_id_offset - 1

        self.__data["view_container"].sort(key=lambda x: x["id"])
        self.__save_json()

    def back(self, status: int):
        self.__status = status
        self.__update_view()

    def model_is_needed(self, number: int):
        model = next(
            (m for m in self.__data["model_container"] if m["id"] == number), None
        )
        if model:
            db_model = model["model_db"]
            json_model = model["model_json"]
            model_instance = self.__get_model_instance(json_model, db_model)
            self.__controller.get_model(model_instance)


# root = CTk()
# # Example usage
# a = MainController("json", "gui", root)
# a.register_view("Enterance_SIGN_Controller", "GUI_owner_customer_enterance", "Terminal_owner_customer_enterance", "sign")
# a.register_view("owner_choice_controller", "gui_owner_menu", "terminal_owner_menu", "owner")
# a.register_view("customer_controller", "gui_get_customer_order", "terminal_get_customer_oreder", "customer")
# a.register_model("DATA_BASE_model","JSON_model")
# a.register_model("DB_FoodModel", "JSON_FoodModel")
# a.register_model("DB_ProductModel", "JSON_ProductModel")
# root.mainloop()
