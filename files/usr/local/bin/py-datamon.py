#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A data-collector and monitor for sensor data.
#
# The program reads data from a file or from stdin (use filename "-"). If
# you want to process data from a serial input, configure the serial line
# and pipe the date to stdin of this program.
#
# stty -F /dev/ttyUSB0 921600
# py-datamon.py -c myconf.json -m - < /dev/ttyUSB0
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import locale, time, os, sys, json, traceback, signal, threading
from   argparse import ArgumentParser
from   pathlib  import Path

# --- application class   ----------------------------------------------------

class App(object):

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self._stop_event = threading.Event()
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
    parser.add_argument('-o', '--output', nargs=1, metavar='output',
      help='output-file')

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

    self._graphs = []
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
      self._graphs = json.load(f)
      f.close()
      self.msg("App: found configuration for %d graphs" % len(self._graphs))
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

  # --- run application   ----------------------------------------------------

  def run(self):
    """ run application """

    # setup signal-handler
    signal.signal(signal.SIGTERM, self.signal_handler)
    signal.signal(signal.SIGINT,  self.signal_handler)

    self.msg("App: running...")

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create application-class, read configuration and run
  app = App()
  if not app.read_config():
    sys.exit(3)
  app.run()
  signal.pause()
  app.cleanup()
