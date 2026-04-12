#! /usr/bin/env python3

# NOTE: sync to webapi/PNAPI/Constants.pm

DEF_CONF_NAME = "../common/config.json"
# keep format compatible with number (e.g. not include hyphen) for easy sorting to find nearby file(s) from any time only by lt/gt comparison
DEF_FMT_DATE = "%Y%m%d"
DEF_FMT_FULL = "%Y%m%d%H%M%S"
DEF_FLIST = "imglist"
DEF_IMG_DNAME = "/image/"
DEF_MOV_DNAME = "/movie/"
DEF_TIMEOUT = 1.5 # HTTP query timeout, default to 1.5sec
DEF_CONF_RELOAD = 600 # configuration file reload per 10min
