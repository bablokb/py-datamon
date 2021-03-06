# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMConfigX: configuration data for x-value
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import types

# --- configuration-object for x-value   -------------------------------------

class DMConfigX(types.SimpleNamespace):
  def __init__(self,app,conf):

    self.msg = app.msg

    # set defaults
    self.col       = 0
    self.type      = "plain"
    self.format    = None       # ignored unless date/datime + live-plot
    self.normalize = False
    self.scale     = 1

    # override with data from config-file
    super(DMConfigX,self).__init__(**conf)

    if self.format is None and self.type in ["date","datetime"]:
      if self.type == "datetime":
        self.format = "%x %X"
      else:
        self.format = "%x"
