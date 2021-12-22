#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# A data-collector and monitor for sensor data.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import locale, time, os, sys, json, threading, signal
from   argparse import ArgumentParser

# --- application class   ----------------------------------------------------

class App(object):

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

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
    parser.add_argument('-f', '--freq', nargs=1, metavar='freq',
      default=0.5, help='update frequency')

    parser.add_argument('-c', '--config', nargs=1, metavar='conf',
      default=0, help='config-file')
    parser.add_argument('-o', '--output', nargs=1, metavar='output',
      default=0, help='output-file')

    parser.add_argument('-d', '--debug', action='store_true',
      dest='debug', default=False,
      help="force debug-mode")
    parser.add_argument('-q', '--quiet', action='store_true',
      dest='quiet', default=False,
      help="don't print messages")
    parser.add_argument('-h', '--help', action='help',
      help='print this help')

    parser.add_argument('input', nargs=1, metavar='input',
      default=0, help='input-file')

    return parser

  # --- print message   ------------------------------------------------------

  def msg(self,text,force=False):
    """ print message """

    if force:
      sys.stderr.write("%s\n" % text)
    elif self.debug:
      sys.stderr.write("[DEBUG %s] %s\n" % (time.strftime("%H:%M:%S"),text))
    sys.stderr.flush()

  # --- setup signal handler   ------------------------------------------------

  def signal_handler(self,_signo, _stack_frame):
    """ signal-handler for clean shutdown """

    self.msg("App: received signal, stopping program ...")
    self.cleanup()

  # --- cleanup ressources   -------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

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

  # create client-class and parse arguments
  app = App()
  app.run()
  signal.pause()
  app.cleanup()
