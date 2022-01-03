# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMPlot: plot data using matplotlib
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import matplotlib.pyplot as plt

# --- class DMPLot   ---------------------------------------------------------

class DMPlot:
  """ plot data using matplotlib """


  # --- constructor   --------------------------------------------------------

  def __init__(self,app,config,data=None,queue=None,stop_event=None):
    """ constructor """

    self.msg         = app.msg
    self._config     = config
    self._data       = data
    self._queue      = queue
    self._stop_event = stop_event

  # --- plot the data   ------------------------------------------------------

  def plot(self):
    """ plot the data """

    # define grid of plots
    fig, axs = plt.subplots(nrows=self._config.rows, ncols=self._config.cols,
                            squeeze=False)

    # add data to plots
    pos = [[r,c] for r in range(self._config.rows)
                                            for c in range(self._config.cols)]
    for [r,c],cfg in zip(pos,self._config.plots):
      self.msg("DMPLot: plotting subplot[%d][%d]" % (r,c))
      for value in cfg.values:
        axs[r][c].plot(self._data[self._config.x.col],self._data[value.col])

    # show plot
    plt.show()
    plt.pause(1)
