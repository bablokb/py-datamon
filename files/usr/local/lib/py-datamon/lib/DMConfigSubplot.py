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
from lib import DMConfigValue, DMConfigAxis, DMConfigX

# --- configuration-object for subplots   ------------------------------------

class DMConfigSubplot(types.SimpleNamespace):
  def __init__(self,app,cfg_plot,conf):

    self.msg = app.msg

    # set defaults
    self.title      = ""
    self.title_opts = {}
    self.options    = {}
    self.legend     = cfg_plot.legend
    self.x          = cfg_plot.x
    self.xaxis      = cfg_plot.xaxis
    self.yaxis      = cfg_plot.yaxis
    self.yaxis2     = cfg_plot.yaxis2
    self.grid       = cfg_plot.grid
    self.grid_opts  = cfg_plot.grid_opts

    # override with data from config-file
    super(DMConfigSubplot,self).__init__(**conf)

    # fix attributes if defaults were overridden
    if not isinstance(self.x,DMConfigX):
      self.x  = DMConfigX(app,self.x)
    if not isinstance(self.xaxis,DMConfigAxis):
      self.xaxis = DMConfigAxis(app,self.xaxis)
    if not isinstance(self.yaxis,DMConfigAxis):
      self.yaxis = DMConfigAxis(app,self.yaxis)
    if self.yaxis2 and not isinstance(self.yaxis2,DMConfigAxis):
      self.yaxis2 = DMConfigAxis(app,self.yaxis2)

    # parse configuration for y-values
    self.msg("DMConfigSubplot: parsing config for %d y-values" % len(self.values))
    self.values = [DMConfigValue(app,value) for value in self.values]

    if isinstance(self.title,dict):
      self.title_opts = self.title
      self.title      = self.title_opts['text']
      del self.title_opts['text']

    if isinstance(self.grid,dict):
      self.grid_opts = self.grid
      self.grid      = self.grid_opts['visible']
      del self.grid_opts['visible']
