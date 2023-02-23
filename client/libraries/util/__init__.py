from collections import defaultdict
import threading
from concurrent.futures import Future
import copy
import json
import multiprocessing
import traceback

# https://stackoverflow.com/a/41274937
class AttributeDict(defaultdict):
  def __init__(self):
    super(AttributeDict, self).__init__(AttributeDict)

  def __getattr__(self, key):
    try:
      return self[key]
    except KeyError:
      raise AttributeError(key)

  def __setattr__(self, key, value):
    self[key] = value

def str_has_numbers(string):
  return any(character.isdigit() for character in string)

# https://stackoverflow.com/a/26426030
class ExceptionThread(threading.Thread):
  def __init__(self, callback=None, *args, **kwargs):
    """
    Redirect exceptions of thread to an exception handler.

    :param callback: function to handle occured exception
    :type callback: function(thread, exception)
    :param args: arguments for threading.Thread()
    :type args: tuple
    :param kwargs: keyword arguments for threading.Thread()
    :type kwargs: dict
    """
    self._callback = callback
    super().__init__(*args, **kwargs)

  def run(self):
    try:
      if self._target:
        self._target(*self._args, **self._kwargs)
    except BaseException as e:
      if self._callback is None:
        raise e
      else:
        self._callback(self, e)
    finally:
      # Avoid a refcycle if the thread is running a function with
      # an argument that has a member that points to the thread.
      del self._target, self._args, self._kwargs, self._callback
      
def merge_dicts(custom, default):
  custom = copy.deepcopy(custom)
  default = copy.deepcopy(default)
  if isinstance(default, dict) and isinstance(custom, dict):
    for k, v in custom.items():
        if k not in default:
          default[k] = v
        else:
          default[k] = merge_dicts(default[k], v)
  return default

def set_config(path, value, default_config = None):
  if default_config != None:
    value = merge_dicts(value, default_config)
  with open(path, "w") as f:
    json.dump(value, f)

def load_config(path, default_config):
  data = None
  try:
    with open(path) as f:
      data = json.load(f)
  except FileNotFoundError:
    set_config(path, default_config)
    data = default_config
  
  out = merge_dicts(data, default_config)
  set_config(path, out)
  return out