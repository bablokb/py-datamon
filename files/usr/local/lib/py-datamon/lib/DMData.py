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

import sys, csv, threading, select
import pandas as pd
import numpy as np

# --- data management for the application   ----------------------------------

class DMData:
  """ data holder and management """

  # --- constructor   --------------------------------------------------------

  def __init__(self,app):
    """ constructor """

    self.msg     = app.msg
    self.debug   = app.debug
    self._config = app.config
    self._wait   = app.WAIT_INTERVAL

    # set defaults

    self.new_data      = False
    self.lock          = threading.Lock()
    self._data         = None
    self._min_max      = None
    self._data_labels  = None
    self._index_low    = 0
    self._index_high   = -1
    self._x_low        = -1

  # --- get item   -----------------------------------------------------------

  def __getitem__(self,key):
    """ return slice of data """

    with self.lock:
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
      return csv.Sniffer().sniff(line).delimiter,line
    else:
      with open(file,'rt') as csvfile:
        line = csvfile.readline().rstrip('\n')
        return self._get_delim(line=line)

  # --- guess if words contain data or a header   ----------------------------

  def _check_header(self,words):
    """ check for csv-header: assume that no field is numeric """

    for word in words:
      try:
        float(word)          # if this does not trigger a ValueError
        return 0             # we have a dataline and should not skip any rows
      except ValueError:
        pass                 # check next word
    return 1                 # no numeric field, so skip one line

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
      fd_ready = select.select(read_list,[],[],self._wait)[0]
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

    # check for initial state
    if self._data is None:
      # guess delimiter and split line
      self._delim,_ = self._get_delim(line=line)
      self.msg("DMData: delimiter is: '%s'" % self._delim)
      words = line.split(self._delim)

      # estimate buffer size and create numpy-buffer
      if self._config.samples:
        n = self._config.samples
      elif self._config.width:
        n = self._config.width
      else:
        n = 500
      self.msg("DMData: create numpy-buffer with %d records" % n)
      self._data    = np.zeros((n,len(words)))
      self._min_max = np.zeros((3,len(words)))

      # check for header
      if self._check_header(words) == 1:
        self.msg("DMData: dropping csv-header: %r" % (words,))
        self._data_labels = words
        return

    # self._data already exists
    else:
      words = line.split(self._delim)

    # convert data
    try:
      data_line = [float(word) for word in words]
      self._scale_record(data_line)
    except ValueError:
      self.msg("DMData: failed to convert: %s" % line)
      return

    # resize numpy-buffer if necessary
    if self._index_high == self._data.shape[0]:
      self._resize_buffer()

    # add data to dataset
    with self.lock:
      # track min and max
      if self._index_high == 0:
        self._min_max[0] = data_line
        self._min_max[1] = data_line
      else:
        self._min_max[2] = data_line                 # current sample
        self._min_max[0] = self._min_max.min(axis=0) # update minimum
        self._min_max[1] = self._min_max.max(axis=0) # update maximum

      # roll data if necessary
      if self._index_high == self._data.shape[0]-1:
        self._data = np.roll(self._data,-1,0)
      else:
        self._index_high += 1

      # finally save new observation
      self.new_data = True
      self._data[self._index_high,:] = data_line

  # --- resize numpy-buffer   ------------------------------------------------

  def _resize_buffer(self):
    """ resize numpy buffer """

    pass

  # --- scale and normalize record   -----------------------------------------

  def _scale_record(self,record):
    """ scale and normalize single record """

    # normalize data (i.e. first observation to timestamp = 0)
    if self._config.x.normalize:
      if self._x_low < 0:
        self._x_low = record[0]
      record[0] -= self._x_low

    # scale data (eg. from ms to s)
    if self._config.x.scale != 1:
      record[0] *= self._config.x.scale

  # --- scale and normalize x-axis data   ------------------------------------

  def _scale_x(self):
    """ scale and normalize x-axis data """

    # normalize data (i.e. first observation to timestamp = 0)
    if self._config.x.normalize:
      x_low = self._data[0,self._config.x.col]
      self._data[:,self._config.x.col] -= x_low

    # scale data (eg. from ms to s)
    if self._config.x.scale != 1:
      self._data[:,self._config.x.col] *= self._config.x.scale

  # --- read data from csv-file   --------------------------------------------

  def import_file(self,file):
    """ read data from csv file """

    self.msg("DMData: reading data from %s" % file)
    delim,line = self._get_delim(file=file)
    self.msg("DMData: delimiter is: '%s'" % delim)

    # check for header line: no field is numeric
    words = line.split(delim)
    skiprows = self._check_header(words)

    if skiprows == 1:
      self.msg("DMData: dropping csv-header: %r" % (words,))
      self._data_labels = words

    # using pandas to read the data, because it is more robust
    # then np.genfromtxt ...
    self._data = pd.read_csv(file,header=None,skiprows=skiprows,sep=delim)
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
