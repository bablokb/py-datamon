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

    # get key for ts-scale
    dict_map = {'s': 'seconds','ms': 'milliseconds', 'us': 'microseconds'}
    self._scale_key = dict_map[self.ts_scale]

    # fix values
    self.columns = int(self.columns)
    self.ts_col  = int(self.ts_col)
    
  # --- cmdline-parser   -----------------------------------------------------

  def _get_parser(self):
    """ configure cmdline-parser """

    parser = ArgumentParser(add_help=False,description='Python Datareader')

    parser.add_argument('-c', '--columns', metavar='columns',
      help='expected number of colums')
    parser.add_argument('-t', '--ts-col', metavar='ts_col',
      default=0, help='column of timestamp (default: 0)')
    parser.add_argument('-s', '--ts-scale', metavar='ts_scale',
                        choices=['s','ms','us'],
                        default='ms',
                        help='timestamp-scale s|ms|us (default: ms)')

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

    # make sure the open call does not block
    if self.input == "-":
      self.msg("App: reading data from stdin")
      read_list = [sys.stdin]
    else:
      self.msg("App: reading data from %s" % self.input)
      fd = os.open(self.input,os.O_RDONLY|os.O_NONBLOCK)
      read_list = [os.fdopen(fd)]

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
      self._ts_1 = datetime.datetime.now()             # save unix-time of 1st line
      self.sep   = csv.Sniffer().sniff(line).delimiter # check for delimiter
      self.msg("App: delimiter is: %s" % self.sep)
      words = line.split(self.sep)
      if len(words) != self.columns:
        self.msg("App: ignoring incomplete line: %d" % self._linenr,force=True)
        return
      else:
        self._first = False
        self._linenr -= 1
        self._offset = float(words[self.ts_col])
        self._handle_line(line)
        return

    # split line and check if line is complete
    words = line.split(self.sep)
    if len(words) != self.columns:
      self.msg("App: ignoring incomplete line: %d" % self._linenr,force=True)
      return
    # calculate timestamp and add column
    delta = float(words[self.ts_col]) - self._offset
    ts = self._ts_1 + datetime.timedelta(**{self._scale_key:delta})
    print("%s%s%f" % (line,self.sep,ts.timestamp()),flush=True)
      
      
# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # create client-class and parse arguments
  app = App()
  app.run()
  signal.pause()
  app.cleanup()
