import requests
import sqlite3

import os
from os.path import join, dirname
from dotenv import load_dotenv


class GeneralAttributes:
    def __init__(self, name, uuid, description, unit):
        self.aname = name
        self.auuid = uuid
        self.adescription = description
        self.aunit = unit
        self.all = [uuid, name, description, unit]


class PartAttributes:
    def __init__(self, value, max_value, min_value, unit, description, ad, an, adesc, aun):
        self.value = value
        self.max_value = max_value
        self.min_value = min_value
        self.unit = unit
        self.description = description

        self.part_attribute_uuid = ad
        self.part_attribute_name = an
        self.part_attribute_description = adesc
        self.part_attribute_units = aun

        self.all = [value, max_value, min_value, unit, description]


class Satsearch:
    # Setting the API access codes.
    def __init__(self, app_id, api_token, column_width=10):
        self.app_id = app_id
        self.token = api_token
        self.column_width = column_width
        self.print_it = 0
        self.debug = 0
        self.all_attributes = {}
        self.part_attributes = {}

        self.name = "No name"
        self.summary = "No summary"
        self.uuid = "No uuid"
        self.last_modified = "No modification date"
        self.supplier = "No supplier"
        self.iterator = 0

        self.aname = ""
        self.adescription = ""
        self.aunit = ""
        self.auuid = 0

        self.value = 0
        self.maximum_value = 0
        self.minimum_value = 0
        self.description = 0
        self.measurement_unit = 0

        self.part_attribute_uuid = ""
        self.part_attribute_name = ""
        self.part_attribute_description = ""
        self.part_attribute_units = ""

        self.get = {}

        self.read_db()

    def get_url(self, url_type, uuid):
        url = "https://api.satsearch.co/v1/" + url_type
        print(url)
        if uuid is not False:
            url = url + "/" + uuid
        response = requests.get(url, headers={"Authorization": "Bearer " + self.token, "X-APP-ID": self.app_id})
        if response.status_code != 200:
            print("ERROR code", response.status_code)
        return response.json()

    def debug_variable_info(self, data, level):
        if self.debug > 0:
            if type(data) is str:
                print("STRING ", end="")
            elif type(data) is dict:
                add_indent(level)
                print("DICT with keys: ", end="")
                keys = list(data.keys())
                print(keys)
            elif type(data) is list:
                print("LIST ")

    def set_length(self, variable):
        if len(variable) < self.column_width:
            whitespace = self.column_width - len(variable)
            variable = variable + " "*whitespace
            return variable
        else:
            return variable

    def get_part(self, uuid, print_data=0):
        if len(uuid) > 15 and print_data:  # To check if we actually have a part and not a service or supplier
            print("VALUE      MIN_VAL    MAX_VAL    UNIT       DESCRIPTION")
            print("----------------------------------------------------------------")
        self.print_it = print_data
        self.properties(self.get_url("products", uuid), 0)

    def print_all(self, uuid):
        self.print_all_sub(self.get_url("products", uuid), 0)

    def print_supplier(self, uuid):
        self.print_all_sub(self.get_url("suppliers", uuid), 0)

    # function for getting the list of all suppliers.
    def print_supplier_list(self):
        self.print_all_sub(self.get_url("suppliers", False), 1)

    def print_attributes_to_db(self):
        conn = sqlite3.connect('attributes.db')
        c = conn.cursor()
        sql = "CREATE TABLE IF NOT EXISTS attributes (uuid text, name text, unit text, description text)"
        c.execute(sql)
        conn.commit()
        self.column_width = 40
        print("At least this works")
        self.read_attributes(self.get_url("products/attributes", False), 1)
        self.column_width = 20

    def print_products_list(self):
        self.print_all_sub(self.get_url("products", False), 1)

    def print_all_sub(self, data, level):
        if type(data) is str:
            self.debug_variable_info(data, level)
            print(data)
        elif type(data) is list:
            self.debug_variable_info(data, level)
            for row in range(0, len(data)):
                add_indent(level)
                print(" -- ", end="")
                self.print_all_sub(data[row], level)

        elif type(data) is dict:
            keys = list(data.keys())

            self.debug_variable_info(data, level)

            for row in range(0, len(keys)):
                add_indent(level)
                name = keys[row]
                info = data[keys[row]]

                if level == 0:
                    print("", end="\n\n\n")

                if self.debug > 0:
                    print("NEW ", end="")
                    print("SUB"*level, end="")
                    print("SECTION: ", end="")

                print(name, end="")

                if type(info) is str:
                    print(": ", end="")
                    self.print_all_sub(info, level)
                elif type(info) is dict or type(info) is list:
                    print("", end="\n")
                    self.print_all_sub(info, level+1)
                else:
                    print("")
        else:
            print("Houston, we have a problem")
            print("Its seems we don't have either a str, dict or list but rather a ", end="")
            print(type(data))

    def read_attributes(self, data, level):
        if type(data) is str:
            self.debug_variable_info(data, level)
        elif type(data) is list:
            self.debug_variable_info(data, level)
            for row in range(0, len(data)):
                self.read_attributes(data[row], level)

        elif type(data) is dict:
            keys = list(data.keys())

            self.debug_variable_info(data, level)

            for row in range(0, len(keys)):
                name = keys[row]
                info = data[keys[row]]

                if level > 0:
                    if name == "name":
                        self.aname = str(info)
                    elif name == "uuid":
                        self.auuid = info
                    elif name == "description":
                        self.adescription = info
                    elif name == "allowed_measurement_units":
                        self.aunit = info
                    if self.aunit != 0 and self.adescription != 0 and self.aname != 0 and self.auuid != 0:
                        self.aname = self.aname.replace(' ', '_')
                        print(list_to_string(self.aunit), self.set_length(self.aname), end="")
                        print(self.set_length(self.auuid), self.set_length(self.adescription))
                        conn = sqlite3.connect('attributes.db')
                        c = conn.cursor()

                        sql = "INSERT INTO attributes VALUES('" + str(self.auuid) + "','" + str(self.aname) + "','"
                        sql = sql + list_to_string(self.aunit) + "','" + str(self.adescription) + "')"
                        c.execute(sql)
                        conn.commit()
                        self.aunit = 0
                        self.adescription = 0
                        self.aname = 0
                        self.auuid = 0

                if type(info) is str:
                    self.read_attributes(info, level)
                elif type(info) is dict or type(info) is list:
                    self.read_attributes(info, level+1)
                else:
                    print("")
        else:
            print("Houston, we have a problem")
            print("Its seems we don't have either a str, dict or list but rather a ", end="")
            print(type(data))

    def read_db(self):
        conn = sqlite3.connect('attributes.db')
        c = conn.cursor()
        for row in c.execute('SELECT * FROM attributes'):
            self.all_attributes[row[0]] = GeneralAttributes(row[1], row[0], row[3], row[2])

    # A function for neatly printing the characteristics of a part in a table.
    def properties(self, data, level):
        if type(data) is list:
            for row in range(0, len(data)):
                self.properties(data[row], level)

        elif type(data) is dict:
            keys = list(data.keys())

            self.debug_variable_info(data, level)

            for row in range(0, len(keys)):
                name = keys[row]
                info = data[keys[row]]
                if level == 0:
                    if name == "name" and self.iterator == 0:
                        self.name = info
                        self.iterator = 1
                    if name == "uuid":
                        self.uuid = info
                    if name == "last_modified":
                        self.last_modified = info
                    if name == "supplier_name":
                        self.supplier = info
                    if name == "summary":
                        self.summary = info
                if level > 0:
                    if name == "value":
                        self.value = info
                        if info == "":
                            self.value = "/"
                    elif name == "minimum_value":
                        self.minimum_value = info
                        if info == "":
                            self.minimum_value = "/"
                    elif name == "maximum_value":
                        self.maximum_value = info
                        if info == "":
                            self.maximum_value = "/"
                    elif name == "measurement_unit":
                        self.measurement_unit = info
                        if info == "":
                            self.measurement_unit = "/"
                    elif name == "description":
                        self.description = info
                        if info == "":
                            self.measurement_unit = "/"
                    elif name == "class":
                        # This code gets the attributes of the part attribute.
                        self.part_attribute_uuid = info['uuid']
                        self.part_attribute_name = info['name']
                        self.part_attribute_description = info['description']
                        self.part_attribute_units = info['allowed_measurement_units']

                        # This gets all the info about the part attribute and the attributes of attribute itself
                        # and places them into the PartAttribute class.

                        part_attribute = PartAttributes(self.value, self.maximum_value, self.minimum_value,
                                                        self.measurement_unit, self.description,
                                                        self.part_attribute_uuid, self.part_attribute_name,
                                                        self.part_attribute_description, self.part_attribute_units)

                        if self.print_it:
                            print(self.set_length(self.value), self.set_length(self.minimum_value),
                                  self.set_length(self.maximum_value), self.set_length(self.measurement_unit),
                                  self.part_attribute_description)

                        if self.part_attribute_uuid in self.all_attributes.keys():
                            name = self.all_attributes[self.part_attribute_uuid].aname
                            print(name)
                            self.get[name] = part_attribute
                if type(info) is str:
                    self.properties(info, level)
                elif type(info) is dict or type(info) is list:
                    self.properties(info, level+1)


def list_to_string(list_to_convert):
    text = ""
    for x in range(0, len(list_to_convert)):
        text += list_to_convert[x] + ", "
    if len(text) < 55:
        whitespace = 55 - len(text)
        text = text + " " * whitespace
        return text
    else:
        return text


def add_indent(level):
    print("\t"*level, end="")


# set up api-code and app-token from .env file located next to this python file.
def get_codes():
    try:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        app_id = os.getenv('APP_ID')
        token = os.getenv('API_TOKEN')
        return [app_id, token]
    except:
        return "couldn't load the .env file..."


part = Satsearch(get_codes()[0], get_codes()[1])
part.get_part("5df368dc-d93f-52bf-beff-896152078722", True)
part.print_all("5df368dc-d93f-52bf-beff-896152078722")
print(part.get['mass'].all)
print(part.get['angular_speed'].all)
# part.print_attributes_to_db()
# print(part.attributes["mass"].all)
