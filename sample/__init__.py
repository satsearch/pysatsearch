import requests


debug = 0


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

    def get_url(self, url_type, uuid):
        url = "https://api.satsearch.co/v1/" + url_type
        if uuid is not False:
            url = url + "/" + uuid
        response = requests.get(url, headers={"Authorization": "Bearer " + self.token, "X-APP-ID": self.app_id})
        if response.status_code != 200:
            print("ERROR code", response.status_code)
        return response.json()

    def debug_variable_info(self, data, level, debug):
        if debug > 0:
            if type(data) is str:
                print("STRING ", end="")
            elif type(data) is dict:
                add_indent(level)
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

    def part_properties(self, uuid, print_data=0):
        if len(uuid) > 15 and print_data:
            print("VALUE      MAX_VAL    MIN_VAL    UNIT       DESCRIPTION")
            print("----------------------------------------------------------------")
        self.print = print_data
        self.properties(self.get_url("products", uuid), 0, debug)

    def print_all(self, uuid):
        self.print_all_sub(self.get_url("products", uuid), 0, debug)

    def print_supplier(self, uuid):
        self.print_all_sub(self.get_url("suppliers", uuid), 0, debug)

    # function for getting the list of all suppliers.
    def print_supplier_list(self):
        self.print_all_sub(self.get_url("suppliers", False), 1, debug)

    def print_products_list(self):
        self.print_all_sub(self.get_url("products", False), 1, debug)

    def print_all_sub(self, data, level, debug_bool):
        if type(data) is str:
            self.debug_variable_info(data, level, debug_bool)
            print(data)
        elif type(data) is list:
            self.debug_variable_info(data, level, debug_bool)
            for row in range(0, len(data)):
                self.add_indent(level)
                print(" -- ", end="")
                self.print_all_sub(data[row], level, debug_bool)

        elif type(data) is dict:
            keys = list(data.keys())

            self.debug_variable_info(data, level, debug_bool)

            for row in range(0, len(keys)):
                self.add_indent(level)
                name = keys[row]
                info = data[keys[row]]

                if level == 0:
                    print("", end="\n\n\n")

                if debug > 0:
                    print("NEW ", end="")
                    print("SUB"*level, end="")
                    print("SECTION: ", end="")

                print(name, end="")
                if type(info) is str:
                    print(": ", end="")
                    self.print_all_sub(info, level, debug)
                elif type(info) is dict or type(info) is list:
                    print("", end="\n")
                    self.print_all_sub(info, level+1, debug_bool)
                else:
                    print("")
        else:
            print("Houston, we have a problem")
            print("Its seems we don't have either a str, dict or list but rather a ", end="")
            print(type(data))

    # A function for neatly printing the characteristics of a part in a table.
    def properties(self, data, level, debug):
        if type(data) is list:
            for row in range(0, len(data)):
                self.properties(data[row], level, debug)

        elif type(data) is dict:
            keys = list(data.keys())

            self.debug_variable_info(data, level, debug)

            for row in range(0, len(keys)):
                name = keys[row]
                info = data[keys[row]]
                if level > 0:
                    if name == "value":
                        self.value = info
                        if info == "":
                            self.value = "/"
                        self.value = self.set_length(self.value)
                    elif name == "minimum_value":
                        self.minimum_value = info
                        if info == "":
                            self.minimum_value = "/"
                        self.minimum_value = self.set_length(self.minimum_value)
                    elif name == "maximum_value":
                        self.maximum_value = info
                        if info == "":
                            self.maximum_value = "/"
                        self.maximum_value = self.set_length(self.maximum_value)
                    elif name == "measurement_unit":
                        self.measurement_unit = info
                        if info == "":
                            self.measurement_unit = "/"
                        self.measurement_unit = self.set_length(self.measurement_unit)
                    if level == 2:
                        if name == "description":
                            self.description = info
                            if self.print == 1:
                                print(self.value, self.maximum_value, self.minimum_value, self.measurement_unit, self.description)

                if type(info) is str:
                    self.properties(info, level, debug)
                elif type(info) is dict or type(info) is list:
                    self.properties(info, level+1, debug)


ss = Satsearch("18a15813704205b3cf2ebeb364aa2ed246a9ed143b6911de4a52cb6045a0049ad1c951a6e8943e3dbc8c5c2c4242a447AbJtXh3J6aazkWKpCRz3nMut6Wu1YCWoEQESOin6qvkeqeDshqw0onjlA7dfM+3n", "ed33aeacabfa6f700faaae3113c6a20f5415f26a53fcde7a4a3bf6437328bdc72950cc5c923fcae2eda85799f7fe9330AkJwB+84zzkIR+glEhYTJ5c5W/6iLMTM5Lzf9HX/uOkK0YjyZZtRoS6sx+Ld6cv3")
ss.part_properties("5df368dc-d93f-52bf-beff-896152078722", True)
ss.part_properties("attributes")
ss.print_all("5df368dc-d93f-52bf-beff-896152078722")
ss.print_supplier_list()
ss.print_supplier("5xf308dc-d93f-52bf-beff-896152078722")
ss.print_products_list()