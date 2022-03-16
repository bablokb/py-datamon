# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMConfigAxis: configuration data for an axis
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import types

# --- configuration-object for y-values   ------------------------------------

class DMConfigAxis(types.SimpleNamespace):
  def __init__(self,app,conf):

    self.msg = app.msg

    # set defaults
    self.axis      = 1
    self.text      = ""
    self.min       = None
    self.max       = None
    self.rescale   = {"max": "*2.0", "min": "*2.0"}
    self.text_opts = {}
    self.options   = {}

    # override with data from config-file
    if isinstance(conf,dict):
      super(DMConfigAxis,self).__init__(**conf)
    else:
      super(DMConfigAxis,self).__init__(text=conf)

    if isinstance(self.text,dict):
      self.text_opts = self.text
      self.text      = self.text_opts['text']
      del self.text_opts['text']

    if isinstance(self.rescale,str):
      self.rescale = {"max": self.rescale, "min": self.rescale}
    self.rescale = types.SimpleNamespace(**self.rescale)

    # convert special attributes to options
    if hasattr(self,"color") and not 'color' in self.text_opts:
      self.text_opts['color'] = self.color
      del self.color
