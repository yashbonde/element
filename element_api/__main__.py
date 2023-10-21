import importlib
from fire import Fire

import uvicorn
from fastapi import FastAPI

from .core import Element, create_app

def echo(*args, **kwargs):
  string = " ".join([str(x) for x in args] + [f"{k}={v}" for k, v in kwargs.items()])
  print(string)

def serve(
  module: str,
  host: str = "0.0.0.0",
  port: int = 6969,
):
  """Serve any python module as a REST API using FastAPI and uvicorn

  Args:
    module (str): The module to serve
    host (str): The host to serve on
    port (int): The port to serve on
  """
  module = importlib.import_module(module)
  module = Element(module)
  app = create_app(module)

if __name__ == '__main__':
  Fire({"echo": echo, "serve": serve})
