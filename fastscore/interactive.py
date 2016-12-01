
import readline
import thread

import service
import dispatch

words = []

def complete(text, state):
  global words, matches
  if state == 0:
    matches = [ w for w in words if w.startswith(text) ]
  if state < len(matches):
    return matches[state]
  return None

def loop():
  if "proxy-prefix" in service.options:
    start_pneumo_feed()
    
  readline.set_completer(complete)
  readline.parse_and_bind("tab: complete")
  try:
    while True:
      line = raw_input("> ")
      if line != "":
        dispatch.run(line.split())
  except EOFError:
    print

def start_pneumo_feed():
  def notify():
    ws = pneumo.connect()
    while True:
      x = json.loads(ws.recv())
      pneumo.print_message(x)
  thread.start_new_thread(notify, ())

