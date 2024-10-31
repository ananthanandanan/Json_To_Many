import csv
import io
from .base_converter import BaseConverter
from ..utils.constants import DEFAULT_ENCODING
from ..utils.json_utils import flatten_json


class JsonToCSV(BaseConverter):
    def __init__(self, data):
        super().__init__(data)
        self.csv_data = []
        self.fieldnames = []
        self.converted_data = None

    def converter(self):
        # Ensure data is a list of dictionaries
        if isinstance(self.data, dict):
            self.data = [self.data]
        elif not isinstance(self.data, list):
            raise ValueError(
                "Invalid JSON data: Expected a dictionary or a list of dictionaries."
            )

        # Flatten each item in the data
        self.csv_data = [flatten_json(item) for item in self.data]
        self.fieldnames = self.get_fieldnames(self.csv_data)
        self.converted_data = self.generate_csv_string()

    def get_fieldnames(self, data):
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        return list(fieldnames)

    def generate_csv_string(self):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.fieldnames)
        writer.writeheader()
        for item in self.csv_data:
            writer.writerow({key: item.get(key, "") for key in self.fieldnames})
        return output.getvalue()

    def save_to_file(self, file_name):
        with open(file_name, "w", newline="", encoding=DEFAULT_ENCODING) as csvfile:
            csvfile.write(self.converted_data)

    def get_converted_data(self):
        """
        Returns the converted CSV data as a string.
        """
        return self.converted_data
