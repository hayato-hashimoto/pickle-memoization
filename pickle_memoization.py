from functools import wraps
import subprocess
import os
import pickle
import hashlib
import inspect
import sys

class digester_wrapper:
  def __init__(self, digester):
    self.digester = digester
    self.digested = []
  def update(self, name, obj):
    self.digested.append(name)
    self.digester.update(obj)
  def hexdigest(self, *args, **kwargs):
    return self.digester.hexdigest(*args, **kwargs)
  
def hash_object(m, name, obj):
  if name in m.digested:
    pass
  elif inspect.isfunction(obj):
    m.update(name, pickle.dumps(inspect.getsource(obj)))
    depends = obj.__code__.co_names
    for d in depends:
      if d in obj.__globals__:
        hash_object(m, d, obj.__globals__[d])
  else:
    try:
      m.update(name, pickle.dumps(obj))
    except:
      pass

def memoize(cachedir):
  cachedir = os.path.expanduser(cachedir)
  def _memoize(func):
    @wraps(func)
    def wrap(*args, **kwargs):
      m = digester_wrapper(hashlib.md5())
      hash_object(m, func.__qualname__, func)
      argnames, varargnames, kwargnames, defaults = inspect.getargspec(func)
      files = ( args[argnames.index('files')] if 'files' in argnames else []+
                [ args[argnames.index('file')]] if 'file' in argnames else []+
                [ args[argnames.index('path')]] if 'path' in argnames else []+
                kwargs['files'] if 'files' in kwargs else []+ 
                [ kwargs['file']] if 'file' in kwargs else [] +
                [ kwargs['path']] if 'path' in kwargs else [])
      for f in files:
        m.digester.update(subprocess.check_output(["md5sum", f]))
      hash_object(m, "**", (args, kwargs, defaults))
      cachefile = os.path.join(cachedir, m.hexdigest())
      if os.path.exists(cachefile):
        print('Reading from "{}" memoizing {}...'.format(cachefile, func.__qualname__), file=sys.stderr)
        with open(cachefile, "rb") as f:
          result = pickle.load(f)
          print("Done", file=sys.stderr)
          return result
      else:
        result = func(*args, **kwargs)
        print('Saving to "{}" memoizing {}...'.format(cachefile, func.__qualname__), file=sys.stderr)
        with open(cachefile, "wb") as f:
          pickle.dump(result, f)
        print("Done", file=sys.stderr)
        return result
    return wrap
  return _memoize
