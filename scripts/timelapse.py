#! /usr/bin/env python3

import sys
import os
import json
import datetime
import subprocess
import shutil

DEF_CONF_NAME = "../common/config.json"
DEF_FMT_DATE = "%Y%m%d"
DEF_FMT_FULL = "%Y%m%d%H%M%S"
DEF_FLIST = "imglist"
DEF_IMG_DNAME = "/image/"
DEF_MOV_DNAME = "/movie/"

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

def BuildImgList(base, dir, ext):
  img_list = []
  alldir = os.listdir(base + dir)
  ext = "." + ext
  for fname in alldir:
    if fname.endswith(ext) and os.path.getsize(base + dir + "/" + fname) > 0:
      img_list.append(fname)
  img_list.sort()
  with open(base + dir + "/" + DEF_FLIST, 'w') as flist:
    for fname in img_list:
      flist.write("file '{}'\n".format(fname))

def ExecVideoBuild(dir, t_date):
  cmd = ["ffmpeg", "-f", "concat", "-i", "./{}/{}/{}".format(DEF_IMG_DNAME, t_date, DEF_FLIST), "-r",
         "10", "-an", "-crf", "28", "-c:v", "libx265", "-preset", "veryfast", "-pix_fmt", "yuv420p", 
         "./{}/{}.mp4".format(DEF_MOV_DNAME, t_date)]
  subprocess.run(cmd, cwd = dir)

def DeleteOld(dir, t_del):
  deldir = dir + "/" + DEF_IMG_DNAME + "/" + t_del
  shutil.rmtree(deldir)

if __name__ == "__main__":
  o_conf = ""
  dt = datetime.datetime.now()
  dt -= datetime.timedelta(days = 1)
  t_date = dt.strftime(DEF_FMT_DATE)
  if len(sys.argv) == 1:
    o_conf = DEF_CONF_NAME
  elif len(sys.argv) == 2:
    o_conf = sys.argv[1]
  elif len(sys.argv) == 3:
    o_conf = sys.argv[1]
    t_date = sys.argv[2]
  else:
    raise Exception("Invalid parameter: command (<target_config>) (<target_date>)")
  c_debug = os.getenv('DEBUG')
  if c_debug != None:
    _debug_level = 1
    _debug = lambda *args: _DebugPrint(*args)
  run_conf = LoadConfig(o_conf)
  if run_conf["storage"][-1] != "/":
    run_conf["storage"] += "/"
  dt -= datetime.timedelta(days = run_conf["keepimage"] - 1)
  t_del = dt.strftime(DEF_FMT_DATE)
  for tgt in run_conf["targets"].keys():
    BuildImgList(run_conf["storage"] + tgt, DEF_IMG_DNAME + t_date, run_conf["targets"][tgt]["ext"])
    ExecVideoBuild(run_conf["storage"] + tgt, t_date)
    DeleteOld(run_conf["storage"] + tgt, t_del)
