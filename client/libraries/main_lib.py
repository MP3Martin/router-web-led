import requests
from time import sleep
from libraries.util import AttributeDict
from libraries.util import ExceptionThread
import traceback

should_exit = False

queue = False

# Globals
CONFIG = AttributeDict()
CONFIG.SERVER_IP = "http://192.168.1.2"
CONFIG.SERVER_PATH = "/cgi-bin/router_led_web.sh"
CONFIG.LED_COUNT = 8
CONFIG.PASSWORD = "whentheimposterissus"
CONFIG.TIMEOUT = 1
CONFIG.DELAY = 0.2
CONFIG.SYNC = 0

# Functions
def stop(e = None, async_ = False):
  global should_exit
  should_exit = True
  if e != None:
    # print(f"Error: Can't connect to host: {e}", file=sys.stderr, flush=True)
    pass
  try:
    set_all_led(0, (not async_), True)
  except Exception:
    pass
  exit()

# def set_led(led, state):
#   payload = {"pass": CONFIG.PASSWORD, "led": str(led), "state": str(state)}
#   response = requests.get(f"{CONFIG.SERVER_IP}/cgi-bin/cmd", params=payload)

def set_frame(leds, sync = False, force_run = False):
  def start():
    if (not should_exit) or (force_run):
      payload = {"pass": CONFIG.PASSWORD, "led": str("".join([ str(i) for i in leds ])), "mode": "1"}
      response = requests.get(f"{CONFIG.SERVER_IP}{CONFIG.SERVER_PATH}", params=payload, timeout=CONFIG.TIMEOUT)
  def err(*args):
    # stop(args[1])
    # stop()
    if queue != False:
      try:
        queue.put({"error": (str(args[0]), str(args[1]))})
      except Exception:
        pass
    # os._exit(0)
    # exit()
    # sys.exit(0)
  if not sync:
    ExceptionThread(err, target=start, daemon=True).start()
  else:
    t = ExceptionThread(err, target=start, daemon=True)
    t.start()
    t.join()

def set_all_led(state, sync = False, force_run = False):
  set_frame([state for _ in range(CONFIG.LED_COUNT)], sync, force_run)
  
def init():
  global led_frame
  global right
  led_frame = [1] + [0 for _ in range(CONFIG.LED_COUNT - 1)]
  right = 1

def gen_frame(mode):
  global led_frame
  global right
  if mode == 0:
    if led_frame[0] == 1:
      right = 1
    elif led_frame[-1:] == [1]:
      right = 0
    if right == 1:
      led_frame = led_frame[-1:] + led_frame[:-1]
    else:
      led_frame.append(led_frame[0])
      led_frame = led_frame[1:]
  elif mode == 1:
    led_frame = led_frame[-1:] + led_frame[:-1]
  elif mode == 2:
    led_frame.append(led_frame[0])
    led_frame = led_frame[1:]
  return led_frame

def main_(mode, config, do_stop = False, do_stop_async = False, queue_ = False):
  global CONFIG
  CONFIG.SERVER_IP = str(config["server_ip"])
  CONFIG.SERVER_PATH = str(config["server_path"])
  CONFIG.LED_COUNT = int(config["led_count"])
  CONFIG.PASSWORD = str(config["password"])
  CONFIG.TIMEOUT = float(config["timeout"])
  CONFIG.DELAY = float(config["delay"])
  CONFIG.SYNC = (int(config["sync"]) == 1)
  
  global queue
  queue = queue_
  
  init()
  if not do_stop:
    while should_exit != True:
      frame = gen_frame(mode)
      set_frame(frame, CONFIG.SYNC)
      sleep(CONFIG.DELAY)
  else:
    stop(None, do_stop_async)
    
def main(*args, **kwargs):
  try:
    main_(*args, **kwargs)
  except (Exception, ValueError, SystemExit):
    queue = args[4]
    if queue != False:
      try:
        queue.put({"error": (str(traceback.format_exc()), "")})
      except Exception:
        pass