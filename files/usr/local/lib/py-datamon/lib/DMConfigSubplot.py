# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMConfigSubplot: configuration data for subplots
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import types
from lib import DMConfigValue

# --- configuration-object for subplots   ------------------------------------

class DMConfigSubplot(types.SimpleNamespace):
  def __init__(self,app,conf):

    self.msg = app.msg

    # set defaults
    self.title      = ""
    self.title_opts = {}
    self.options    = {}
    self.legend     = {"loc": "best"}

    # override with data from config-file
    super(DMConfigSubplot,self).__init__(**conf)

    # parse configuration for y-values
    self.msg("DMConfigSubplot: parsing config for %d y-values" % len(self.values))
    self.values = [DMConfigValue(app,value) for value in self.values]

    if isinstance(self.title,dict):
      self.title_opts = self.title
      self.title      = self.title_opts['text']
      del self.title_opts['text']
