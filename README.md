# Element

Instantly create API endpoints for any python module, use those as client or ignore everything written before.

```
pip install element_api
```

Internet applications are tediously hard to write and so I created `element` (abstracting from `fire`) that can serve and query any python module. Let's just say you want to convert python package `os` into an RPC, this is so easy:

```python
from element_api import Element

import os

# [local]
# use the package as you were using it and forget that there is anything in between
os = Element(os)
os.path.exists("./test.py") # >>> False

# [server]
# you can serve by adding a few lines to your script
from element_api import convert_to_app
os = Element(os)
app = convert_to_app(os)
# in shell/docker $ uvicorn myfile:app
# http://0.0.0.0:5000

# [client]
# you can query the above server
os = Element(os, url = "http://0.0.0.0:5000")
os.path.exists("./test.py") # >>> True
```
