# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMConfigPlot: configuration data for plots
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import types, math
from lib import DMConfigSubplot, DMConfigValue, DMConfigAxis

# --- configuration-object for plots   ---------------------------------------

class DMConfigPlot(types.SimpleNamespace):

  # --- constructor   --------------------------------------------------------

  def __init__(self,app,conf):
    """ constructor """

    self.msg = app.msg
    
    # set defaults
    self.title      = ""
    self.title_opts = {}
    self.options    = {"constrained_layout": True}
    self.legend     = {"loc": "best"}
    self.cols       = 1
    self.xaxis      = {"text": "time (ms)"}
    self.yaxis      = {"text": "value"}

    # override with data from config-file
    super(DMConfigPlot,self).__init__(**conf)

    # set axis
    self.x     = types.SimpleNamespace(**self.x)
    self.xaxis = DMConfigAxis(app,self.xaxis)
    self.yaxis = DMConfigAxis(app,self.yaxis)

    # parse configuration for subplots
    self.msg("DMConfigPlot: parsing config for %d subplots" % len(self.plots))
    self.plots = [DMConfigSubplot(app,self,plot) for plot in self.plots]

    self._get_layout()
    self.msg("DMConfigPlot: subplot-layout is %dx%d" % (self.rows,self.cols))

    # convert special attributes to options
    if hasattr(self,"width") and hasattr(self,"height"):
      self.options['figsize'] = (self.width/100,self.height/100)
      self.options['dpi']     = 100

    if isinstance(self.title,dict):
      self.title_opts = self.title
      self.title      = self.title_opts['text']
      del self.title_opts['text']

  # --- calculate layout   ---------------------------------------------------

  def _get_layout(self):
    """ calculate layout """

    if not hasattr(self,"rows"):
      self.rows = math.ceil(len(self.plots)/self.cols)
