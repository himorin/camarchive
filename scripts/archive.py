#! /usr/bin/env python3

import sys
import os
import json
import time
import datetime
import requests

DEF_CONF_NAME = "../common/config.json"
DEF_FMT_DATE = "%Y%m%d"
DEF_FMT_FULL = "%Y%m%d%H%M%S"
DEF_IMG_DNAME = "/image/"

_debug = lambda *args: None
_debug_level = 0

def LoadConfig(conf_name):
  try:
    fjson = open(conf_name, 'r')
  except IOError as e:
    raise Exception("File '%s' open error: %s" % (conf_name, e))
  try:
    run_conf = json.load(fjson)
  except:
    raise Exception("json format parse error for '%s'" % (conf_name))
  return run_conf

def _DebugPrint(msg):
  c_now = datetime.now().replace(microsecond = 0)
  print("{}: {}".format(c_now.isoformat(), msg))

def CalcNearbyStartTime(interval):
  ct = datetime.datetime.now()
  ctsec = ct.hour * 3600 + ct.minute * 60 + ct.second
  ctdel = interval - (ctsec % interval)
  return ct + datetime.timedelta(seconds = ctdel, microseconds = - ct.microsecond)

def ArchiveImage(f_head, dname, fname, conf):
  save_to = f_head + "/" + dname + "/"
  os.makedirs(save_to, exist_ok = True)
  save_to += fname + "." + conf["ext"]
  # requests
  opt = {}
  if ("user" in conf) and ("pass" in conf):
    opt["auth"] = (conf["user"], conf["pass"])
  try:
    o_res = requests.get(conf["url"], **opt)
    if o_res.status_code != requests.codes.ok:
      return
    if o_res.headers["Content-Type"].split("/")[0] != "image":
      return
    with open(save_to, 'wb') as fd:
      for chunk in o_res.iter_content(chunk_size=128):
        fd.write(chunk)
  except Exception as e:
    _debug("Failed to archive image (%s): %s" % (save_to, e))

if __name__ == "__main__":
  o_conf = ""
  if len(sys.argv) == 1:
    o_conf = DEF_CONF_NAME
  elif len(sys.argv) == 2:
    o_conf = sys.argv[1]
  else:
    raise Exception("Invalid parameter: command (<target_config>)")
  c_debug = os.getenv('DEBUG')
  if c_debug != None:
    _debug_level = 1
    _debug = lambda *args: _DebugPrint(*args)
  run_conf = LoadConfig(o_conf)
  run_next = CalcNearbyStartTime(run_conf["interval"])
  run_delta = datetime.timedelta(seconds = run_conf["interval"])
  f_head = run_conf["storage"]
  while True:
    # sleep until next start (not exactly)
    time.sleep((run_next - datetime.datetime.now()).total_seconds())
    dname = run_next.strftime(DEF_FMT_DATE)
    fname = run_next.strftime(DEF_FMT_FULL)
    run_next += run_delta
    for tgt in run_conf["targets"].keys():
      # XXX: for now, no thread used here
      ArchiveImage(f_head, tgt + DEF_IMG_DNAME + dname, fname, run_conf["targets"][tgt])

