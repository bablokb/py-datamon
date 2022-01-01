#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A data-collector and monitor for sensor data.
#
# The program reads data from a file or from stdin (use filename "-"). If
# you want to process data from a serial input, configure the serial line
# and pipe the date to stdin of this program.
#
# stty -echo -F /dev/ttyUSB0 115200
# py-datamon.py -c myconf.json -m - < /dev/ttyUSB0
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import locale, time, os, sys, json, traceback, signal, threading, select
import queue
from   argparse import ArgumentParser
from   pathlib  import Path

import pandas as pd

# --- application imports   --------------------------------------------------

libdir = Path(sys.argv[0]).parent / "../lib/py-datamon"
sys.path.append(str(libdir))

from lib import DMPlot, DMConfigPlot

# --- application class   ----------------------------------------------------

class App:

  # --- constants   ----------------------------------------------------------

  WAIT_INTERVAL = 1     # interval to check for stop-event

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self.is_live     = False

    self._threads    = []
    self._stop_event = threading.Event()
    self._data       = None
    parser = self._get_parser()
    parser.parse_args(namespace=self)

  # --- cmdline-parser   -----------------------------------------------------

  def _get_parser(self):
    """ configure cmdline-parser """

    parser = ArgumentParser(add_help=False,description='Python Datamonitor')

    parser.add_argument('-m', '--monitor', action='store_true',
                        dest='monitor', default=False,
                        help='start real-time monitor')
    parser.add_argument('-p', '--plot', action='store_true',
                        dest='plot', default=False,
                        help='create plots (png)')
    parser.add_argument('-f', '--freq', metavar='freq',
      default=0.5, help='update frequency')

    parser.add_argument('-c', '--config', metavar='conf',
      help='config-file')

    parser.add_argument('-d', '--debug', action='store_true',
      dest='debug', default=False,
      help="force debug-mode")
    parser.add_argument('-q', '--quiet', action='store_true',
      dest='quiet', default=False,
      help="don't print messages")
    parser.add_argument('-h', '--help', action='help',
      help='print this help')

    parser.add_argument('input', metavar='input',help='input-file')

    return parser

  # --- read data   ----------------------------------------------------------

  def _read_data(self):
    """ read data and add it to a queue """

    # make sure the open call does not block
    if self.input == "-":
      self.msg("App: reading data from stdin")
      read_list = [sys.stdin]
    else:
      self.msg("App: reading data from %s" % self.input)
      fd = os.open(self.input,os.O_RDONLY|os.O_NONBLOCK)
      read_list = [os.fdopen(fd)]

    self._data_queue = queue.Queue()
    while read_list:
      fd_ready = select.select(read_list,[],[],App.WAIT_INTERVAL)[0]
      if self._stop_event.is_set():
        self.msg("App: request to stop reading")
        break
      if fd_ready:
        line = fd_ready[0].readline().rstrip('\n')
        #self.msg("App: input line: %s" % line)
        if not line:             # EOF, remove file from input list
          read_list.clear()
        elif line.rstrip():      # optional: skipping empty lines
          # process line
          self._data_queue.put(line)

    self.msg("App: no more input, stopping program")
    os.kill(os.getpid(), signal.SIGINT)

  # --- print message   ------------------------------------------------------

  def msg(self,text,force=False):
    """ print message """

    if force:
      sys.stderr.write("%s\n" % text)
    elif self.debug:
      sys.stderr.write("[DEBUG %s] %s\n" % (time.strftime("%H:%M:%S"),text))
    sys.stderr.flush()

  # --- read configuration   --------------------------------------------------

  def read_config(self):
    """ read configuration-file, if supplied """

    if self.config:
      p = Path(self.config)
      if not p.exists() and not p.is_absolute():
        # try in default location
        p = Path(sys.argv[0]).parent / "../lib/py-datamon/configs" / self.config
        if not p.exists():
          self.msg("App: config-file %s does not exist" % self.config,True)
          return False
    else:
      # use default
      p = Path(sys.argv[0]).parent / "../lib/py-datamon/configs/default.json"

    try:
      self.msg("App: reading configuration from %s" % str(p))
      f = open(p,"r")
      plot = json.load(f)
      f.close()
      self.config = DMConfigPlot(self,plot)
      return True
    except:
      self.msg("App: reading configuration from %s failed" % str(p),True)
      if self.debug:
        traceback.print_exc()
      return False

  # --- setup signal handler   ------------------------------------------------

  def signal_handler(self,_signo, _stack_frame):
    """ signal-handler for clean shutdown """

    self.msg("App: received signal, stopping program ...")
    self.cleanup()

  # --- cleanup ressources   -------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """

    self._stop_event.set()

    map(threading.Thread.join,self._threads)
    self.msg("App: ... finished")

  # --- read data   ----------------------------------------------------------

  def _read(self):
    """ read data from csv (synchronously) or from pipe/device (async) """

    if self.input != "-" and Path(self.input).is_file():
      # just import the csv-data directly
      self.msg("App: reading data from %s" % self.input)
      self._data = pd.read_csv(self.input,header=None)
      if any(self._data.iloc[0].apply(lambda x: isinstance(x, str))):
        self.msg("App: dropping csv-header")
        self._data = self._data[1:].reset_index(drop=True)
      if self.debug:
        print("-"*75)
        print(self._data.head(10))
        print("-"*75)
    else:
      # use a reader-thread if we are reading from a pipe or device
      self.is_live = True
      reader_thread = threading.Thread(target=self._read_data)
      reader_thread.start()
      self._threads.append(reader_thread)

  # --- plot the data   ------------------------------------------------------

  def _plot(self):
    """ plot the data """

    if self.is_live:
      plotter = DMPlot(self,self.config,queue=self._data_queue,
                                                 stop_event=self._stop_event)
      plotter_thread = threading.Thread(target=plotter.plot)
      plotter_thread.start()
      self._threads.append(plotter_thread)
    else:
      plotter = DMPlot(self,self.config,data=self._data)
      plotter.plot()

  # --- run application   ----------------------------------------------------

  def run(self):
    """ run application """

    self._read()
    self.msg("App: running ...")
    self._plot()

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create application-class, read configuration
  app = App()
  if not app.read_config():
    sys.exit(3)

  # setup signal handlers
  signal.signal(signal.SIGTERM,app.signal_handler)
  signal.signal(signal.SIGINT,app.signal_handler)

  # run application threads
  app.run()
  if app.is_live:
    signal.pause()
