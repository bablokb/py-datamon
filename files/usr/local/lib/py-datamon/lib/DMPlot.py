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
import matplotlib.animation as animation

# --- class DMPLot   ---------------------------------------------------------

class DMPlot:
  """ plot data using matplotlib """


  # --- constructor   --------------------------------------------------------

  def __init__(self,app,config,data=None,stop_event=None):
    """ constructor """

    self.msg         = app.msg
    self._img_file   = app.output
    self._freq       = app.freq
    self._config     = config
    self._data       = data
    self._stop_event = stop_event

  # --- update the plot-data   -----------------------------------------------

  def _update(self,have_new):
    """ update-function for animation """

    self.msg("DMPLot: _update with have_new: %r" % have_new)
    if have_new:
      i = 0
      for plot_cfg in self._config.plots:
        for value in plot_cfg.values:
          self._lines[i].set_data(self._data[plot_cfg.x.col],     # synchronized in
                                  self._data[value.col])          # DMData
          i += 1
      return self._lines
    else:
      return []

  # --- check for new data   -------------------------------------------------

  def _check_new(self):
    """ frames-function for animation """

    while True:
      with self._data.lock:
        have_new = self._data.new_data
        self._data.new_data = False
      yield have_new

  # --- plot the data   ------------------------------------------------------

  def plot(self):
    """ plot the data """

    # define grid of plots
    fig, axs = plt.subplots(nrows=self._config.rows, ncols=self._config.cols,
                            squeeze=False,**self._config.options)
    fig.suptitle(self._config.title,**self._config.title_opts)

    # create list of subplot-coordinates
    pos = [[r,c] for r in range(self._config.rows)
                                            for c in range(self._config.cols)]

    # list of Line2D-artists (needed for live-monitoring)
    if self._config.is_live:
      self._lines = []

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
        line = axs[r][c].plot(self._data[plot_cfg.x.col],
                              self._data[value.col],
                              label = value.label,
                              **value.options)
        axs[r][c].set_title(plot_cfg.title,**plot_cfg.title_opts)
        if self._config.is_live:
          self._lines.append(line[0])

      # ... plot legend
      if plot_cfg.legend["loc"]:
        axs[r][c].legend(**plot_cfg.legend)

    # show plot
    if self._img_file:
      plt.savefig(self._img_file)
      self.msg("DMPlot: %s created" % self._img_file,force=True)
    else:
      if self._config.is_live:
        ani = animation.FuncAnimation(fig,
                                      self._update,
                                      self._check_new,
                                      interval=self._freq,
                                      blit=True)
        plt.show()
      else:
        plt.show()
        plt.pause(1)
