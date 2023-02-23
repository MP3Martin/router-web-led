from textual.app import App, ComposeResult
from textual import events
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.reactive import var, reactive
from textual.widgets import Button, Static, Input, ListView, ListItem, Label, Header, Footer, Switch, Markdown
from textual.widget import Widget
from textual.screen import Screen

from rich.traceback import Traceback

from libraries.util import str_has_numbers
from libraries.util import load_config
from libraries.util import set_config
import os
import time
import sys
from multiprocessing import Process, Queue
import libraries.main_lib as main_lib

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

modes = (
  (0, "Side to side", "A dot moves from side to side."),
  (1, "Left to right", "A dot moves from left to right."),
  (2, "Right to left", "A dot moves from right to left.")
)

default_config = {
  "server_ip": "http://192.168.1.1",
  "server_path": "/cgi-bin/router_led_web.sh",
  "led_count": "8",
  "password": "whentheimposterissus",
  "timeout": "1",
  "delay": "0.2",
  "sync": "0"
}

configs = (
  ("Server IP", "The ip of the server (router).", "server_ip"),
  ("Server path", "Web path to the script on the server.", "server_path"),
  ("LED count", "The number of LEDs on your router.", "led_count"),
  ("Password", "You have set this in your server's .sh script.", "password"),
  ("Timeout", "Server counts as unreachable after this time (seconds).", "timeout"),
  ("Delay", "Time between frames (in seconds).", "delay"),
  ("Synchronous (0 or 1)", "If the frames are sent synchronously or not.", "sync")
)

config_location = os.path.join(__location__, "config.json")

def select_mode(self, mode_id):
  try:
    switch = self.query_one(f".mode_switch_{mode_id}", Switch)
    switch.focus()
    switch.toggle()
  except:
    pass

class Configs(Static):
  config = reactive(load_config(config_location, default_config))
  def compose(self):
    for config_option in configs:
      yield Container(
        Static(f"[yellow]{config_option[0]}: [/yellow]"),
        Input(
          placeholder = config_option[1], password=(config_option[0].lower() == "password"),
          value=f"{self.config[config_option[2]]}", classes="configs_input", id=f"configs_input_{config_option[2]}"),
        classes="configs_container"
      )
    yield Container(
      Button(
        "Save config",
        variant="primary",
        id="save_config_button"
      ),
      id="save_config_wrapper"
    )
  
  def watch_config(self, new_config):
    for input_ in self.query(".configs_input"):
      input_keyname = input_.id.replace("configs_input_", "")
      try:
        input_.value = self.config[input_keyname]
      except:
        pass

class ErrorText(Static):
  error = reactive(None)
  def on_mount(self):
    self.update_timer = self.set_interval(1 / 10, self.update_error) # 10 times a second
  def update_error(self):
    self.error = self.ancestors[-1].query_one(State).error_text
  def watch_error(self, new_error):
    try:
      if new_error == None:
        self.ancestors[-1].add_class("hide_errortext")
      else:
        self.ancestors[-1].remove_class("hide_errortext")
    except:
      pass
    if new_error != None:
      self.update(f"Error: {new_error[0]}\n{new_error[1]}")

class StateText(Static):
  state = reactive(0)
  switch_state = False
  def on_mount(self):
    self.update_timer = self.set_interval(1 / 10, self.update_state) # 10 times a second
  def update_state(self):
    # Try to get error
    if self.ancestors[-1].query_one(State).queue != None:
      try:
        err = self.ancestors[-1].query_one(State).queue.get_nowait()
        err = err["error"]
        self.ancestors[-1].query_one(State).process.kill()
        self.ancestors[-1].query_one(State).queue = None
        self.ancestors[-1].query_one(State).error_text = err
      except:
        pass
        
    try:
      if (self.ancestors[-1].query_one(State).process != None) and (not self.ancestors[-1].query_one(State).process.is_alive()) and (self.ancestors[-1].query_one("#state_toggle").value == True):
        if self.ancestors[-1].query_one(State).error_text == None:
          self.ancestors[-1].query_one(State).error_text = ("Unknown error", "Unknown error")
        self.ancestors[-1].query_one(State).process = None
        self.ancestors[-1].query_one(State).state = -1
      else:
        self.state = self.ancestors[-1].query_one(State).state  
    except:
      pass
    self.switch_state = self.ancestors[-1].query_one("#state_toggle").value
  def get_state_text(self, state):
    if state == 1:
      return "[b][green]ON[/green][/b]"
    elif state == -1:
      return "[b][red]OFF (error)[/red][/b]"
    else:
      return "[b][red]OFF[/red][/b]"
  def watch_state(self, old_state, new_state):
    if old_state == 1 and new_state == -1:
      self.ancestors[-1].query_one("#state_toggle").toggle()
      self.state = -1
    self.update("State: " + self.get_state_text(new_state))

class State(Static):
  queue = var(None)
  _state = reactive(0)
  @property
  def state(self):
    return self._state
  @state.setter
  def state(self, value):
    self._state = value
    self.refresh()
  error = reactive("")
  process = reactive(None)
  error_text = reactive(None)
  
  def led_off(self):
    try:
      main_lib.main(int(self.ancestors[-1].query_one(Modes).mode), self.ancestors[-1].query_one(Configs).config, True, True)
    except:
      pass
  
  def start_process(self, state):
    try:
      if state == True:
        self.error_text = None
        self.state = 1
        self.queue = Queue()
        self.process = Process(target=main_lib.main, args=(int(self.ancestors[-1].query_one(Modes).mode), self.ancestors[-1].query_one(Configs).config, False, False, self.queue))
        self.process.start()
      else:
        if self.ancestors[-1].query_one(State).error_text == None:
          self.state = 0
        try:
          self.process.kill()
          self.led_off()
        except:
          pass
    except Exception as e:
      self.state = -1
      self.error = e
  def compose(self):
    yield Container(
      Container(
        Switch(
          id="state_toggle"
          ),
        StateText(),
        id="state_toggle_wrapper"
      ),
      id="state_container"
    )

class Modes(Static):
  mode = reactive(0)
  def compose(self):
    yield Container(
      Static("[b][#e48311]WARNING:[/#e48311][/b] [#eaa85b]If you update the mode or the config, you need to toggle the state [#ef8146]off[/#ef8146] and [#bfbc46]on[/#bfbc46] again![/#eaa85b]"),
      classes="mode_container mode_warning"
    )
    for mode in modes:
      yield Container(
        Switch(classes=f"mode_switch mode_switch_{mode[0]}", value=(mode[0] == 0)),
        Container(
          Static(
            f"[b][#FF8C00][{mode[0]}][/b][#FF8C00] [cyan]{mode[1]}[/cyan]",
            classes="mode_title"
          ),
          Static(
            f"[i][#8d8d8d]{mode[2]}[/i][/#8d8d8d]",
            classes="mode_description_description"
          ),
          classes="mode_description"
        ),
        classes="mode_container"
      )


class SetRouterLEDApp(App):
  CSS_PATH = "main.css"
  BINDINGS = [
    Binding(key="ctrl+c, q", action="custom_quit", description="Exit"),
    ("[NUMPAD #]", "", "Select mode"),
    Binding(key="t", action="toggle_state", description="Toggle the state")
  ]

  def compose(self):
    yield Header(show_clock = True)
    yield Container(
      Container(
        Configs(),
        id="config_container"
      ),
      Container(
        Modes(),
        id="modes_container"
      ),
      Container(
        State(),
        id="state_container"
      ),
      Container(
        ErrorText(),
        id="errortext_container"
      ),
      # Button("Choose mode...", id="choose_mode"),
      Footer(),
      classes="main_container"
    )
  
  def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "save_config_button":
      config = {}
      config_inputs = self.query(".configs_input")
      for config_input in config_inputs:
        config_input_keyname = config_input.id.replace("configs_input_", "")
        config_input_value = config_input.value
        if config_input_value != "":
          config[config_input_keyname] = config_input_value
      set_config(config_location, config, default_config)
      self.query_one(Configs).config = load_config(config_location, default_config)
      self.query_one(Configs).watch_config(self.query_one(Configs).config)
  
  def on_key(self, event: events.Key):
    key = event.key
    if key.isdecimal():
      select_mode(self, str(key))
    elif key in ["up", "down", "left", "right"]:
      if key in ["up", "down"]:
        switches = list(self.query(".mode_switch"))
        focused_switch = None
        for switch in switches:
          if ("focus-within" in list(switch.pseudo_classes)) and ("focus" in list(switch.pseudo_classes)):
            focused_switch = switch
        if focused_switch == None:
          pass
        else:
          classes = list(focused_switch.classes)
          for class_ in classes:
            if str_has_numbers(class_):
              id_class = class_
          switch_id = int(id_class[-1])
          target_id = None
          if key == "up":
            target_id = switch_id - 1
          elif key == "down":
            target_id = switch_id + 1
          try:
            target = self.query_one(f".mode_switch_{target_id}")
            target.focus()
          except:
            pass
          
  # def on_mount(self):
  #   exit(load_config(os.path.join(__location__, "config.json"), default_config))
    
  def on_switch_changed(self, event):
    classes = list(event.input.classes)
    value = event.value
    focus = "focus" in list(event.input.pseudo_classes)
    if "mode_switch" in classes:
      if value == False: # Better readability than "if not value:" (in this case)
        if focus: # If the switch was toggled by user
          event.sender.toggle()
      else:
        switches = list(self.query(".mode_switch"))
        switches.remove(event.sender)
        for switch in switches:
          if switch.value == True:
            switch.toggle()
        switches = list(self.query(".mode_switch"))
        for switch in switches:
          if switch.value == True:
            classes = list(switch.classes)
            for class_ in classes:
              if str_has_numbers(class_):
                id_class = class_
            switch_id = int(id_class[-1])
            self.query_one(Modes).mode = switch_id
    elif event.input.id == "state_toggle":
      self.query_one(State).start_process(event.input.value)
      
  def action_toggle_state(self):
    state_toggle = self.query_one("#state_toggle")
    state_toggle.focus()
    state_toggle.toggle()
    
  def action_custom_quit(self):
    try:
      # state = self.ancestors[-1].query_one(State).state
      self.query_one(State).process.terminate()
      # if state == 1:
      #   main_lib.main(int(self.query_one(Modes).mode), self.query_one(Configs).config, True)
    except:
      pass
    try:
      if self.ancestors[-1].query_one("#state_toggle").value == True:
        self.ancestors[-1].query_one("#state_toggle").toggle()
    except:
      pass
    self.app.exit()
        

if __name__ == "__main__":
  app = SetRouterLEDApp()
  app.run()