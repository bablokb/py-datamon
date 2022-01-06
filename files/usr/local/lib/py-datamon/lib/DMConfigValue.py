# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMConfigValue: configuration data for y-values
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import types

# --- configuration-object for y-values   ------------------------------------

class DMConfigValue(types.SimpleNamespace):
  def __init__(self,app,conf):

    self.msg = app.msg

    # set defaults
    self.label   = ""
    self.options = {}

    # override with data from config-file
    super(DMConfigValue,self).__init__(**conf)
