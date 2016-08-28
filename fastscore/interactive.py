
import readline
import thread
import ssl
from websocket import create_connection
import json

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
  if "connect-prefix" in service.options:
    connect_notify()
    
  readline.set_completer(complete)
  readline.parse_and_bind("tab: complete")
  try:
    while True:
      line = raw_input("> ")
      if line != "":
        if not dispatch.run(line.split()):
          print "Invalid command - use 'help'"
  except EOFError:
    print

def connect_notify():
  prefix = service.options["connect-prefix"]
  def notify():
    ws = create_connection(prefix.replace("https:", "wss:") + "/1/notify",
                              sslopt={"cert_reqs": ssl.CERT_NONE})
    while True:
      x = json.loads(ws.recv())
      print_notify(x)
  thread.start_new_thread(notify, ())

def print_notify(msg):
  src = msg["src"]
  timestamp = msg["timestamp"]
  type = msg["type"]

  if type == "health":
    print "[%s] %s %s is %s" % \
           (src,
            time_only(timestamp),
            msg["instance"],
            "up" if msg["health"] == "ok" else "DOWN")

  elif type == "log":
    print "[%s] %s [%s] %s" % \
           (src,
            time_only(timestamp),
            level_text(msg["level"]),
            msg["text"])
  elif type == "output-report":
    for x in msg["outputs"]:
      print "[%s] output [%s] %s" % \
           (src,
            msg["model"],
            json.dumps(x))
    skipped = msg["skipped"]
    if skipped > 0:
      print "[%s] %d ouput(s) skipped" % (src,skipped)
  elif type == "model-console":
    print "[%s] %s" % (src,msg["text"]),

  else:
    print json.dumps(msg, indent=2)

def time_only(timestamp):
  return timestamp.split("T")[1].strip("Z")

def level_text(l):
  if   l == 128: return "debug"
  elif l == 64:  return "info"
  elif l == 32:  return "notice"
  elif l == 16:  return "warning"
  elif l == 8:   return "error"
  elif l == 4:   return "critical"
  else:          return str(l)
