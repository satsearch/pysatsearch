from PySatsearch import Satsearch
import os
from os.path import join, dirname
from dotenv import load_dotenv


# set up api-code and app-token
def get_code():
    try:
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        app_id = os.getenv('APP_ID')
        token = os.getenv('API_TOKEN')
        return [app_id, token]
    except:
        return "couldn't load the .env file..."


ss = Satsearch(get_code()[0], get_code()[1])

# Enter into the class the information from a certain uuid (part). The "True" flag means that the program will print
# all the attributes of that part in the terminal.
ss.get_part("5df368dc-d93f-52bf-beff-896152078722", True)
print(ss.attributes["N m s"].all)
print(ss.attributes["kg"].min_value)
print(ss.attributes["N m"].value)
print(ss.attributes["mm"].description)
print(ss.name)
print(ss.supplier)
print(ss.summary)
print(ss.uuid)

# Prints all the information of a part in the terminal
ss.print_all("5df368dc-d93f-52bf-beff-896152078722")

# Prints a list of all suppliers in the terminal
ss.print_supplier_list()

# Prints infrormation about a supplier in the terminal
ss.print_supplier("223b9107-8d85-5b3c-8742-f7f63a67fccf")

# Prints a list of all the products
ss.print_products_list()
