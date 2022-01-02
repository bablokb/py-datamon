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
from lib import DMConfigSubplot

# --- configuration-object for plots   ---------------------------------------

class DMConfigPlot(types.SimpleNamespace):

  # --- constructor   --------------------------------------------------------

  def __init__(self,app,conf):
    """ constructor """

    self.msg = app.msg
    
    # set defaults
    self.title = "Default Title"
    self.cols  = 1

    # override with data from config-file
    super(DMConfigPlot,self).__init__(**conf)

    # parse configuration for subplots
    self.msg("DMConfigPlot: parsing config for %d subplots" % len(self.plots))
    self._subplots = [DMConfigSubplot(app,plot) for plot in self.plots]
    del self.plots

    self._get_layout()

  # --- calculate layout   ---------------------------------------------------

  def _get_layout(self):
    """ calculate layout """

    if not hasattr(self,"rows"):
      self.rows = math.ceil(len(self._subplots)/self.cols)
