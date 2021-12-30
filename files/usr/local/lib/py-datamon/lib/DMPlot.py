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

  def __init__(self,config,data=None,queue=None,stop_event=None):
    """ constructor """

    self._config     = config
    self._data       = data
    self._queue      = queue
    self._stop_event = stop_event

  # --- plot the data   ------------------------------------------------------

  def plot(self):
    """ plot the data """

    # define grid of plots
    fig, axs = plt.subplots(nrows=2, ncols=1)

    # add data to plots
    axs[0].plot(self._data[0],self._data[1])
    axs[1].plot(self._data[0],self._data[2])

    # show plot
    plt.show()
    plt.pause(1)
