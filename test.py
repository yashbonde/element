import os
from pprint import pprint as peepee

from element_api import Element, create_app

print(Element)

# os = Element(os, mode = "server")
# app = create_app(os)

os = Element(os, mode = "client", url = "http://127.0.0.1:8000")
print(os)
print(os.getcwd())


# import os
# from fire import _Fire

# print(_Fire(os, None, None, None))

# os.path
