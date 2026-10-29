import json
import os


DATA_FOLDER = "data"


PRODUCT_FILE = os.path.join(
    DATA_FOLDER,
    "products.json"
)

CUSTOMER_FILE = os.path.join(
    DATA_FOLDER,
    "customers.json"
)

SALES_FILE = os.path.join(
    DATA_FOLDER,
    "sales.json"
)


def create_data_folder():

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)


def load_data(filename):

    create_data_folder()

    if not os.path.exists(filename):
        return []

    try:

        with open(filename, "r") as file:
            data = json.load(file)

            return data

    except (json.JSONDecodeError, FileNotFoundError):

        return []


def save_data(filename, data):

    create_data_folder()

    with open(filename, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )