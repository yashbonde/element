from fire import Fire

def echo(*args, **kwargs):
  string = " ".join([str(x) for x in args] + [f"{k}={v}" for k, v in kwargs.items()])
  print(string)

if __name__ == '__main__':
  Fire({"echo": echo})
