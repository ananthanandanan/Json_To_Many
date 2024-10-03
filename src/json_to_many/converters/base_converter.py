from abc import ABC, abstractmethod


class BaseConverter(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def converter(self):
        pass

    @abstractmethod
    def save_to_file(self, file_name):
        pass

    @abstractmethod
    def get_converted_data(self):
        pass
