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
    self.title = "Default Title"

    # override with data from config-file
    super(DMConfigSubplot,self).__init__(**conf)

    # parse configuration for y-values
    self.msg("DMConfigSubplot: parsing config for %d y-values" % len(self.y))
    self._y = [DMConfigValue(app,y) for y in self.y]
    del self.y
