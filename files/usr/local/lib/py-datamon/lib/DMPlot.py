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

import time
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

  # --- calculate new xmin for plot   ----------------------------------------

  def _new_xmin(self,cfg,xmin,current):
    """ get new minimum for x-axis """

    if cfg.min == "off":
      # keep configured minimum
      return xmin
    elif cfg.min == "auto":
      return current
    elif cfg.min[0] == "*":
      # to slow down flickering, we move the minimum only if
      # current > fac*xmin
      if current > float(cfg.min[1:])*xmin:
        return current
      else:
        return xmin
    elif cfg.min[0] == "+":
      if current > xmin+float(cfg.min[1:]):
        return current
      else:
        return xmin
    else:
      # unsupported
      return current

  # --- calculate new xmax for plot   ----------------------------------------

  def _new_xmax(self,cfg,xmax,current):
    """ get new maximum for x-axis """

    if cfg.max == "off":
      # keep configured maximum
      return xmax
    elif cfg.max == "auto":
      return current
    elif cfg.max[0] == "*":
      # we expect a factor > 1: increase by factor
      return max(10,current,xmax*float(cfg.max[1:]))
    elif cfg.max[0] == "+":
      # linear increase
      return xmax + float(cfg.max[1:])
    else:
      # unsupported
      return current

  # --- calculate new y-limits for plot   ------------------------------------

  def _new_ylim(self,rescale,ymin,ymax,current):
    """ get new limits for y-axis """

    if rescale == "auto":
      return current

    if current < ymin:
      lower = True
    else:
      lower = False

    if rescale == "off":
      # keep configured limit
      return ymin if lower else ymax
    elif rescale[0] == "*":
      # we expect a factor >1: increase interval by factor
      interval = ymax-ymin
      if lower:
        return min(current,ymax-float(rescale[1:])*interval)
      else:
        return max(current,ymin+float(rescale[1:])*interval)
    elif rescale[0] == "+":
      if lower:
        return min(current,ymin-float(rescale[1:]))
      else:
        return max(current,ymax+float(rescale[1:]))
    else:
      # unsupported
      return current

  # --- update the plot-data   -----------------------------------------------

  def _update(self,have_new):
    """ update-function for animation """

    if have_new:
      redraw = False
      i_line = 0
      i_ax   = 0
      for plot_cfg in self._config.plots:
        (ymin,ymax) = self._axs[i_ax].get_ylim()
        (xmin,xmax) = self._axs[i_ax].get_xlim()
        (tmin,tmax) = self._data.minmax(plot_cfg.x.col)

        # handle x-axis scrolling/rescaling
        if tmin > xmin:
          new_min = self._new_xmin(plot_cfg.xaxis.rescale,xmin,tmin)
          if new_min > xmin:
            self._axs[i_ax].set_xlim(left=new_min)
            redraw = True
        if tmax > xmax:
          new_max = self._new_xmax(plot_cfg.xaxis.rescale,xmax,tmax)
          if new_max > xmax:
            self._axs[i_ax].set_xlim(right=new_max)
            redraw = True

        for value in plot_cfg.values:
          # check if a redraw is necessary
          (vmin,vmax) = self._data.minmax(value.col)
          if not plot_cfg.yaxis.min and vmin < ymin:
            new_min = self._new_ylim(plot_cfg.yaxis.rescale.min,ymin,ymax,vmin)
            self._axs[i_ax].set_ylim(bottom=new_min)
            redraw = True
          if not plot_cfg.yaxis.max and vmax > ymax:
            new_max = self._new_ylim(plot_cfg.yaxis.rescale.max,ymin,ymax,vmax)
            self._axs[i_ax].set_ylim(top=new_max)
            redraw = True
          # update values
          self._lines[i_line].set_data(self._data[plot_cfg.x.col], # synchronized in
                                  self._data[value.col])           # DMData
          i_line += 1
        i_ax += 1
      if redraw:
        self._axs[0].figure.canvas.draw()

    # always return the line-artists, or else the animation fails
    return self._lines

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

    # keep list of artists (needed for live-monitoring)
    self._lines = []
    self._axs   = []

    # for every subplot...
    for [r,c],plot_cfg in zip(pos,self._config.plots):
      self._axs.append(axs[r][c])
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

      # wait until data is available
      if self._config.is_live:
        while not self._data.new_data:
          time.sleep(self._freq/1000)

      # ... plot 1..n y-values
      for value in plot_cfg.values:
        line = axs[r][c].plot(self._data[plot_cfg.x.col],
                              self._data[value.col],
                              label = value.label,
                              **value.options)
        axs[r][c].set_title(plot_cfg.title,**plot_cfg.title_opts)
        self._lines.append(line[0])

      # ... plot legend
      if plot_cfg.legend["loc"]:
        axs[r][c].legend(**plot_cfg.legend)

    # show plot
    if self._img_file:
      plt.savefig(self._img_file)
      self.msg("DMPlot: %s created" % self._img_file,force=True)
    elif self._config.is_live:
      ani = animation.FuncAnimation(fig,
                                    self._update,
                                    self._check_new,
                                    interval=self._freq,
                                    blit=True)
      plt.show()
    else:
      plt.show()
      plt.pause(1)
