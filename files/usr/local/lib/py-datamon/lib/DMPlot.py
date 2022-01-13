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
                            squeeze=False,**self._config.options)
    fig.suptitle(self._config.title,**self._config.title_opts)

    # add data to plots
    pos = [[r,c] for r in range(self._config.rows)
                                            for c in range(self._config.cols)]

    # for every subplot...
    for [r,c],plot_cfg in zip(pos,self._config.plots):
      self.msg("DMPLot: plotting subplot[%d][%d]" % (r,c))

      # ... configure axis
      if plot_cfg.xaxis.min:
        axs[r][c].set_xlim(left=plot_cfg.xaxis.min)
      if plot_cfg.xaxis.max:
        axs[r][c].set_xlim(right=plot_cfg.xaxis.max)
      if plot_cfg.yaxis.min:
        axs[r][c].set_ylim(bottom=plot_cfg.yaxis.min)
      if plot_cfg.yaxis.max:
        axs[r][c].set_ylim(top=plot_cfg.yaxis.max)

      # ... and plot axis-label
      axs[r][c].set_xlabel(plot_cfg.xaxis.text,**plot_cfg.xaxis.text_opts)
      axs[r][c].set_ylabel(plot_cfg.yaxis.text,**plot_cfg.yaxis.text_opts)

      # ... and plot grid
      axs[r][c].grid(visible=plot_cfg.grid,**plot_cfg.grid_opts)

      # ... plot 1..n y-values
      for value in plot_cfg.values:
        axs[r][c].plot(self._data[self._config.il:self._config.ih,plot_cfg.x.col],
                       self._data[self._config.il:self._config.ih,value.col],
                       label = value.label,
                       **value.options)
        axs[r][c].set_title(plot_cfg.title,**plot_cfg.title_opts)

      # ... plot legend
      if plot_cfg.legend["loc"]:
        axs[r][c].legend(**plot_cfg.legend)

    # show plot
    plt.show()
    plt.pause(1)
