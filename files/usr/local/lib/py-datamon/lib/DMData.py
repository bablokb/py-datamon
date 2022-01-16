# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMData: The data-management class for the application
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import csv
import pandas as pd

# --- data management for the application   ----------------------------------

class DMData:
  """ data holder and management """

  # --- constructor   --------------------------------------------------------

  def __init__(self,app):
    """ constructor """

    self.msg   = app.msg
    self.debug = app.debug

    # set defaults

    self._data         = None
    self._data_labels  = None
    self._index_low    = 0
    self._index_high   = 0
    self._x_low        = -1

  # --- get item   -----------------------------------------------------------

  def __getitem__(self,key):
    """ return slice of data """

    if isinstance(key,int):
      return self._data[self._index_low:self._index_high,key]
    else:
      return self._data[key[0],key[1]]

  # --- set item   -----------------------------------------------------------

  def __setitem__(self,key,value):
    """ return slice of data """

    if isinstance(key,int):
      self._data[key] = value
    else:
      self._data[key[0],key[1]] = value

  # --- get delimiter of csv-data   ------------------------------------------

  def _get_delim(self,file=None,line=None):
    """ guess delimiter by sniffing the given line """

    if file is None:
      return csv.Sniffer().sniff(line).delimiter
    else:
      with open(file,'rt') as csvfile:
        line = csvfile.readline()
        return self._get_delim(line=line)

  # --- read data   ----------------------------------------------------------

  def _read_continuous(self):
    """ read data and add it to a queue """

    # make sure the open call does not block
    if self._input == "-":
      self.msg("DMData: reading data from stdin")
      read_list = [sys.stdin]
    else:
      self.msg("DMData: reading data from %s" % self._input)
      fd = os.open(self._input,os.O_RDONLY|os.O_NONBLOCK)
      read_list = [os.fdopen(fd)]

    while read_list:
      fd_ready = select.select(read_list,[],[],App.WAIT_INTERVAL)[0]
      if self._stop_event.is_set():
        self.msg("DMData: request to stop reading")
        break
      if fd_ready:
        line = fd_ready[0].readline().rstrip('\n')
        if not line:             # EOF, remove file from input list
          read_list.clear()
        else:
          self._add_data(line.rstrip())

  # --- add data to the internal dataset   -----------------------------------

  def _add_data(self,line):
    """ add data to the dataset """

    if not line:
      return
    self.msg("DMData: new data: %s" % line)

  # --- scale and normalize x-axis data   ------------------------------------

  def _scale_x(self):
    """ scale and normalize x-axis data """

    # normalize data (i.e. first observation to timestamp = 0)
    if self._config.x.normalize:
      if self._x_low < 0:
        self._x_low = self._data[0,self._config.x.col]
      self._data[:,self._config.x.col] -= self._x_low

    # scale data (eg. from ms to s)
    if self._config.x.scale != 1:
      self._data[:,self._config.x.col] *= self._config.x.scale

  # --- set plot-configuration   ---------------------------------------------

  def set_config(self,config):
    """ set plot-configuration """

    self._config = config

  # --- read data from csv-file   --------------------------------------------

  def import_file(self,file):
    """ read data from csv file """

    self.msg("DMData: reading data from %s" % file)
    delim = self._get_delim(file=file)
    self.msg("DMData: delimiter is: '%s'" % delim)

    # using pandas to read the data, because it is more robust
    # then np.genfromtxt ...
    self._data = pd.read_csv(file,header=None,sep=delim)
    if any(self._data.iloc[0].apply(lambda x: isinstance(x, str))):
      self.msg("DMData: dropping csv-header")
      self._data_labels = self._data.iloc[0]
      self._data = self._data[1:].reset_index(drop=True)
    if self.debug:
      self.msg("DMData: total data-rows: %d" % self._data.shape[0])
      print("-"*75)
      print(self._data.head(10))
      print("-"*75)

    # ... but convert to numpy-array, because a dataframe is not
    # thread-safe
    self._data = self._data.to_numpy()

    # set low/high indices (for csv-files, we use the complete data)
    self._index_low  = 0
    self._index_high = self._data.shape[0]

    # normalize and scale data
    self._scale_x()

  # --- start reader thread for dynamic data   -------------------------------

  def start_reader(self,input,stop_event):
    """ start reader thread """

    self._input      = input
    self._stop_event = stop_event

    reader_thread = threading.Thread(target=self._read_continuous)
    reader_thread.start()
    return reader_thread
