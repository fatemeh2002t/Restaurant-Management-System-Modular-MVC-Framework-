from abc import ABC, abstractmethod


class MainInterface:
    @abstractmethod
    def create_widgets(self) -> None:
        pass

    @abstractmethod
    def binding(self) -> None:
        pass

    @abstractmethod
    def pack_forget(self):
        pass

    def set_controller(self, controller) -> None:
        self._controller = controller
        self.create_widgets()
        self.binding()


class sign_in_sign_up_enterance(MainInterface):
    @abstractmethod
    def get_user_name(self) -> str:
        pass

    @abstractmethod
    def get_password(self) -> str:
        pass

    @abstractmethod
    def successful_operation(self):
        pass

    @abstractmethod
    def wrong_operation(self):
        pass

    @abstractmethod
    def clear_entires(self):
        pass


#############################################################################################
class ModelInterface(ABC):

    @abstractmethod
    def represent_report(self) -> bool:
        pass


class customer_owner_model(ModelInterface):
    @abstractmethod
    def __setitem__(self, username: str, password: str) -> None:
        pass

    @abstractmethod
    def create_model(self, role: str) -> None:
        pass

    @abstractmethod
    def authentification(self, username: str, password: str) -> bool:
        pass


###############################################################################################
class ControllerInterface(ABC):
    @abstractmethod
    def __init__(self, main_controller, interface: MainInterface) -> None:
        pass

    # @abstractmethod
    # def back(self):
    #     pass
    @abstractmethod
    def next_mvc(self) -> None:
        pass

    @abstractmethod
    def get_model(self, model: ModelInterface) -> None:
        pass


################################################################################################
