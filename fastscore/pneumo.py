
import service

import ssl
from websocket import create_connection, WebSocketTimeoutException
import json

def connect():
  prefix = service.options["proxy-prefix"]
  ws = create_connection(prefix.replace("https:", "wss:") + "/api/1/service/connect/1/notify",
                         sslopt={"cert_reqs": ssl.CERT_NONE})
  return ws

def watch(args):
  ws = connect()
  try:
    while True:
      x = json.loads(ws.recv())
      print_message(x)
  except KeyboardInterrupt:
    ws.close

def flush(args):
  ws = connect()
  ws.settimeout(1)
  flushed = 0
  try:
    while True:
      ws.recv()
      flushed += 1
  except WebSocketTimeoutException:
    pass
  if flushed > 0:
    print "%d message(s) flushed" % flushed
  ws.close

def list(args):
  print "Type                 | Description"
  print "---------------------|--------------------------"
  print "health               | health status changes"
  print "log                  | a log message"
  print "model-console        | model console output"
  print "jet-status-report    | model runner status info"
  print "output-report        | data produced by a model"
  print "rejected-data-report | data rejected by a stream"
  print "output-eof           | data processing finished"

def wait(args):
  type = args["message-type"]
  ws = connect()
  try:
    while True:
      x = json.loads(ws.recv())
      if x["type"] == type:
        print_message(x)
        break
  except KeyboardInterrupt:
    ws.close

def print_message(msg):
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
      print "[%s] output [%s] %s" % (src,msg["model"],x)
    skipped = msg["skipped"]
    if skipped > 0:
      print "[%s] %d ouput(s) skipped" % (src,skipped)

  elif type == "jet-status-report":
    pass
##    m = [ j["memory"] for j in msg["jets"] ]
##    if len(m) == 1:
##      print "Mem: %s" % mb(m[0])
##    else:
##      print "Mem:",
##      for x in m:
##        print mb(x),
##      print "total %s" % mb(sum(m))

  elif type == "output-eof":
    print "[%s] %s all data processed" % (src,time_only(timestamp))

  elif type == "model-console":
    print "[%s] %s %s" % (src,time_only(timestamp),msg["text"]),

  elif type == "x-jet-info":
    pass # internal profiler messages

  else:
    print json.dumps(msg, indent=2)

def mb(bytes):
  return "%.1fM" % (bytes / 1024 / 1024)

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

