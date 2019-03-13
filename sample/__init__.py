import requests


class Parameter:
    def __init__(self, value, max_value, min_value, unit, description):
        self.value = value
        self.max_value = max_value
        self.min_value = min_value
        self.unit = unit
        self.description = description
        self.all = [value, max_value, min_value, unit, description]


class Satsearch:
    # Setting the API access codes.
    def __init__(self, app_id, api_token, column_width=10):
        self.app_id = app_id
        self.token = api_token
        self.column_width = column_width
        self.measurement_unit = 0
        self.maximum_value = 0
        self.description = 0
        self.value = 0
        self.minimum_value = 0
        self.maximum_value = 0
        self.print = 0
        self.debug = 0
        self.attributes = {}

        self.name = "No name"
        self.summary = "No summary"
        self.uuid = "No uuid"
        self.last_modified = "No modification date"
        self.supplier = "No supplier"
        self.iterator = 0

        self.yr = None
        self.torque = None
        self.momentum = None
        self.mechanical_vibration = None
        self.radiation_tolerance = None
        self.mass = None
        self.power = None
        self.voltage = None
        self.angular_velocity = None
        self.temperature = None

    def get_url(self, url_type, uuid):
        url = "https://api.satsearch.co/v1/" + url_type
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
                self.add_indent(level)
                print("DICT with keys: ", end="")
                keys = list(data.keys())
                print(keys)
            elif type(data) is list:
                print("LIST ")

    def add_indent(self, level):
        print("\t"*level, end="")

    def empty(self, value):
        try:
            value = float(value)
        except ValueError:
            pass
        return bool(value)

    def set_length(self, variable):
        if len(variable) < self.column_width:
            whitespace = self.column_width - len(variable)
            variable = variable + " "*whitespace
            return variable
        else:
            return variable

    def get_part(self, uuid, print_data=0):
        if len(uuid) > 15 and print_data:  # To check if we actually have a part and not a service or supplier
            print("VALUE      MAX_VAL    MIN_VAL    UNIT       DESCRIPTION")
            print("----------------------------------------------------------------")
        self.print = print_data
        self.properties(self.get_url("products", uuid), 0)

    def print_all(self, uuid):
        self.print_all_sub(self.get_url("products", uuid), 0)

    def print_supplier(self, uuid):
        self.print_all_sub(self.get_url("suppliers", uuid), 0)

    # function for getting the list of all suppliers.
    def print_supplier_list(self):
        self.print_all_sub(self.get_url("suppliers", False), 1)

    def print_products_list(self):
        self.print_all_sub(self.get_url("products", False), 1)

    def print_all_sub(self, data, level):
        if type(data) is str:
            self.debug_variable_info(data, level)
            print(data)
        elif type(data) is list:
            self.debug_variable_info(data, level)
            for row in range(0, len(data)):
                self.add_indent(level)
                print(" -- ", end="")
                self.print_all_sub(data[row], level)

        elif type(data) is dict:
            keys = list(data.keys())

            self.debug_variable_info(data, level)

            for row in range(0, len(keys)):
                self.add_indent(level)
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
                    if level == 2:
                        if name == "description":
                            self.description = info
                            print(self.set_length(self.value), self.set_length(self.minimum_value),
                                  self.set_length(self.maximum_value), self.set_length(self.measurement_unit),
                                  self.description)
                            parameter_data = Parameter(self.value, self.maximum_value, self.minimum_value,
                                                       self.measurement_unit, self.description)
                            self.attributes[self.measurement_unit] = parameter_data
                if type(info) is str:
                    self.properties(info, level)
                elif type(info) is dict or type(info) is list:
                    self.properties(info, level+1)
