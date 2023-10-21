import os
import sys
import inspect
import traceback
from requests import Session

from fastapi import FastAPI
from pydantic import create_model
from starlette.requests import Request
from starlette.responses import Response

MODE = os.getenv("PYTHON_ELEMENT_MODE", "local")

def get_spec(fn, prefix = ""):
  # spec gives you the full annotation of the function, what goes in what comes out, etc.
  # here we take this spec and extract or remove things from it.
  try:
    spec = inspect.getfullargspec(fn)
  except TypeError:
    return None
  spec.annotations.pop("return", None)
  
  fields_dict = {k: [str, None] for k in spec.args} # <keyword>: ["type", "default"]
  if spec.defaults:
    for k, v in zip(spec.args[::-1], spec.defaults[::-1]):
      fields_dict[k] = [type(v), v]
  if spec.kwonlydefaults:
    for k, v in spec.kwonlydefaults.items():
      fields_dict[k] = [type(v), v]
  fields_dict = {k: tuple(v) for k, v in fields_dict.items()}
  fields_dict["msg"] = (str, None) # one default for messages

  name = fn.__name__
  RequestModel = create_model(f"{name}_Request", **fields_dict)

  # print(fn.__name__)
  def __wrapper_fn(request: Request, response: Response, request_model: RequestModel):
    data = request_model.dict()
    data.pop("msg", None)
    try:
      output = fn(**data)
      return {"output": output}
    except Exception as e:
      _t = traceback.format_exc()
      response.status_code = 500
      return {"msg": f"command {fn.__name__} failed: {e} | {_t}"}

  path = prefix.rstrip("/") + "/" + fn.__name__
  # print(fn.__name__, path)

  return {
    "path": path,
    "endpoint": __wrapper_fn,
    "methods": ["POST"],
    "name": name,
    "status_code": 200,
    "meta": {
      "request_model": RequestModel,
      "fields_dict": fields_dict
    }
  }


class Element:
  def __init__(self, module, mode = "local", url = "", session = None, root = None):
    self.module = module
    self.mode = mode
    self.url = url.rstrip("/") if isinstance(url, str) else url
    self.session = session

    if mode == "local":
      # in this case there is nothing to be done, except ensure that the computation
      # happens locally
      assert not url and not session, "url and session cannot only be set in 'client' mode"
      pass
    elif mode == "client":
      assert isinstance(url, str) and url.startswith("http"), \
        "correct url is required for client mode"
      if session == None:
        # create a session that can sustain the entire period of this object and
        # inherents the cookies and all that jazz
        self.session = Session()
    elif mode == "server":
      # in this case we need to ensure that url and session are not set and infact
      # this is just another version of local mode, but in the __call__ method it
      # creates a function on the fly and uses it to call the underlying module
      # function
      assert not url and not session, "url and session cannot only be set in 'client' mode"
    else:
      raise ValueError(f"{mode} should be one of 'local', 'client', or 'server'")

    # define routes here, above the below exit
    self.routes = []

    # this simple logic avoids infinite recursion
    # some python modules are straightout screwed up, look at this:
    # os.path.genericpath.os == os # True
    if module.__name__ == root:
      print(module.__name__, root)
      return
    if root == None:
      root = module.__name__
    
    # create the routes
    for fn in dir(module):
      _m = getattr(module, fn)
      _m_name = type(_m).__name__
      if (
        _m_name in ["str", "int", "float", "dict", "bool", "set", "NoneType"] or
        fn in sys.builtin_module_names or
        f"_{fn}" in sys.builtin_module_names or
        fn.startswith("_") or
        _m_name not in ["function", "builtin_function_or_method", "module"]
      ):
        # skip under these conditions
        continue
        
      print("----->>>>>", module, fn, _m, root)

      if callable(_m):
        route = get_spec(_m, self.url)
        if route:
          self.routes.append(route)
      elif _m_name == "module":
        elem = Element(_m, mode, url, session, root)
        print(elem)
        self.routes.extend(elem.routes)

    self.my_route = get_spec(module, self.url)
      
  def __getattr__(self, __name):
    # __getattr__ is called when __name is not found, so don't worry
    # about module, url and session
    obj = getattr(self.module, __name, None)
    if obj == None:
      raise AttributeError(f"{__name} not found in {self.module}")
    
    obj_name = type(obj).__name__
    if obj_name in ["function", "builtin_function_or_method", "module"]:
      return Element(obj, self.mode, self.url + "/" + __name, self.session)
    elif obj_name in ["int", "float", "str"]:
      return obj
    else:
      raise ValueError(__name, obj_name)
          
  def __repr__(self):
    return f"<Element ({self.url}, {self.module}, {self.mode})>"
      
  def __call__(self, *args, **kwargs):
    if not callable(self.module):
      raise TypeError(f"{self.module} is not callable")

    if self.mode == "local":
      return self.module(*args, **kwargs)
    elif self.mode == "client":
      fields_dict = self.my_route["meta"]["fields_dict"]
      data = {}
      for a, k in zip(args, fields_dict):
        data[k] = a
      for k, v in kwargs.items():
        data[k] = v
      print(data)
      model = self.my_route["meta"]["request_model"].parse_obj(data)
      r = self.session.post(self.url, json = model.dict())
      if not r.status_code == 200:
        raise Exception(r.text)
      return r.json()
    elif self.mode == "server":
      pass



# class Element:
#   """Wrap any ``function, builtin_function_or_method, module`` python object such that it can be
#   used cross internet as an RPC, without writing any additional code.

#   Args:
#     module (module): The module to wrap.
#     url (str): The url to use for the RPC, if passed treated in ``CLIENT`` mode
#   """
#   valid = ["function", "builtin_function_or_method"]
#   repeat = ["module"]

#   def __init__(self, module, url = None, prefix = ""):
#     self.module = module
#     self.url = url
#     self.prefix = prefix
#     # self.abspath = inspect.getabsfile(module)
    
#     self._understanding = {}
#     for x in dir(self.module):
#       if x.startswith("_"):
#         continue
#       try:
#         obj_ = getattr(os, x)
#       except AttributeError:
#         continue
#       type_ = type(obj_).__name__
      
#       if type_ in self.valid:
#         element = obj_
#       elif type_ in self.repeat:
#         print("--->", x)
#         if self.module.__name__ in sys.builtin_module_names:
#           continue
#         element = Element(obj_, prefix = self.prefix + "/" + x)
#         print("-" * 70)
#       else:
#         continue

#       self._understanding[x] = {
#         "obj": obj_,
#         "type": type_,
#         "element": element
#       }

#     # print(self._understanding)

#   def __repr__(self):
#     return f"<Element ({self.module.__name__})>"

#   def _routes(self):
#     routes = []
#     for k,v in self._understanding.items():
#       print(self.prefix, k, v)
#       if v["type"] == "function":
#         routes.append(get_spec(v["obj"], self.prefix))
#       elif v["type"] == "module":
#         routes.extend(v["element"]._GetRoutes())
#         print("-" * 70, k)
#     return routes
  
#   def __getattr__(self, __name):
#     if __name.startswith("_") and not __name.startswith("_G"):
#       raise AttributeError(f"Cannot parse items starting with underscore, got: '{__name}'")

#     if __name == "_GetRoutes":
#       return self._routes

# def element(module):
#   return Element(module)

def create_app(e, *fast_api_args, **fast_api_kwargs):
  assert e.mode == "server", "mode should be 'server' when creating app"
  app = FastAPI(*fast_api_args, **fast_api_kwargs)
  for route in e.routes:
    route.pop("meta", None)
    app.add_api_route(**route) 
  return app
