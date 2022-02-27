#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Read data from file (e.g. device) and add timestamp
#
# MCUs without RTC will usually only output a timestamp since boot. This
# program adds an additional column with a true (unix) timestamp. It uses
# the ts of the first line as an offset to have consistent time-data.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import locale, time, os, sys, csv, threading, signal, select, datetime
from   argparse import ArgumentParser

# --- application class   ----------------------------------------------------

class App(object):

  WAIT_INTERVAL = 1     # interval to check for stop-event

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self._stop_event = threading.Event()
    self._first      = True
    self._linenr     = 0
    parser = self._get_parser()
    parser.parse_args(namespace=self)

    # check values
    if not self.columns:
      self.msg("error: need to specify columns (option -c)",force=True)
      sys.exit(3)
    
  # --- cmdline-parser   -----------------------------------------------------

  def _get_parser(self):
    """ configure cmdline-parser """

    parser = ArgumentParser(add_help=False,description='Python Datareader')

    parser.add_argument('-c', '--columns', metavar='columns',
                        type=int, default=0,
                        help='expected number of colums')

    parser.add_argument('-f', '--ts-format', metavar='ts-format',
      dest='ts_format', default='i', nargs='?',
      help="timestamp-format (i=iso, u=unix, or generic format, default: i)")

    parser.add_argument('-d', '--debug', action='store_true',
      dest='debug', default=False,
      help="force debug-mode")
    parser.add_argument('-q', '--quiet', action='store_true',
      dest='quiet', default=False,
      help="don't print messages")
    parser.add_argument('-h', '--help', action='help',
      help='print this help')

    parser.add_argument('input',metavar='input',help='input-file')

    return parser

  # --- print message   ------------------------------------------------------

  def msg(self,text,force=False):
    """ print message """

    if force and not self.quiet:
      sys.stderr.write("%s\n" % text)
    elif self.debug:
      sys.stderr.write("[DEBUG %s] %s\n" % (time.strftime("%H:%M:%S"),text))
    sys.stderr.flush()

  # --- setup signal handler   ------------------------------------------------

  def signal_handler(self,_signo, _stack_frame):
    """ signal-handler for clean shutdown """

    self.msg("App: received signal, stopping program ...")
    self._stop_event.set()
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
    self._process_input()
    sys.exit(0)

  # --- process input   ------------------------------------------------------

  def _process_input(self):
    """ read input, process and output """

    if self.input == "-":
      self.msg("App: reading data from stdin")
      read_list = [sys.stdin]
    else:
      self.msg("App: reading data from %s" % self.input)
      read_list = [open(self.input,buffering=1)]

    eof = False
    while read_list:
      fd_ready = select.select(read_list,[],[],self.WAIT_INTERVAL)[0]
      if self._stop_event.is_set():
        self.msg("App: request to stop reading")
        break
      if fd_ready:
        line = fd_ready[0].readline().rstrip('\n')
        #self.msg("App: line: %s" % line)
        if not line:
          # quit after two consecutive empty lines
          if eof:
            read_list.clear()
          else:
            eof = True
            continue
        else:
          eof = False
          self._handle_line(line.rstrip())

  # --- handle single line   -------------------------------------------------

  def _handle_line(self,line):
    """ process a single line """

    self._linenr += 1
    if self._first:
      self.sep   = csv.Sniffer().sniff(line).delimiter # check for delimiter
      self.msg("App: delimiter is: %s" % self.sep)
      words = line.split(self.sep)
      if len(words) != self.columns or not words[0]:
        self.msg("App: ignoring incomplete line (%d): %s" %
                 (self._linenr,line),force=True)
        return
      else:
        self._first = False
        self._linenr -= 1
        self._handle_line(line)
        return

    # split line and check if line is complete
    words = line.split(self.sep)
    if len(words) != self.columns or not words[0]:
      self.msg("App: ignoring incomplete line (%d): %s" %
               (self._linenr,line),force=True)
      return

    # calculate timestamp and add column
    if self.ts_format == 'i':
      ts = '"{}"'.format(datetime.datetime.now().isoformat())
    elif self.ts_format == 'u':
      ts = str(datetime.datetime.now().timestamp())
    else:
      ts = '"{}"'.format(datetime.datetime.now().strftime(self.ts_format))

    print("%s%s%s" % (line,self.sep,ts),flush=True)
      
      
# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = App()
  app.run()
  signal.pause()
  app.cleanup()
