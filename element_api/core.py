import os
import inspect

MODE = os.getenv("PYTHON_ELEMENT_MODE", "local")

class Element:
  valid = ["function", "builtin_function_or_method"]
  to_analyse = ["builtin_function_or_method"]
  repeat = ["module"]

  def __init__(self, module):
    self.module = module
    self.abspath = inspect.getabsfile(module)
    
    self._understanding = {}
    for x in dir(self.module):
      obj_ = getattr(os, x)
      type_ = type(obj_)
      if type_ in self.valid:
        element = obj_
      elif type_ in self.repeat:
        element = Element(obj_)

      self._understanding[x] = {
        "obj": obj_,
        "type": type_,
        "element": element
      }
          
  def __repr__(self):
    return f"<Element ({self.module.__name__})>"
  
  def __getattr__(self, __name):
    if __name.startswith("_"):
      raise AttributeError(f"Cannot parse items starting with underscore, got: '{__name}'")

