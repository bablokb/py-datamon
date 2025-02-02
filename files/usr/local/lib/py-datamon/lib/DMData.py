# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Class DMData: The data-management class for the application
#
# There are two modes of operation:
#   - synchronous for csv-files, i.e. the DMData.import_file() reads the
#     data and DMPlot later reads the data
#   - asynchronous for live-plots. Here a reader thread continuously
#     reads data into a buffer. DMPlot will call DMData.update() from
#     a second thread to update the internal numpy-array from the buffer
#     whenever the function-animation routine is running
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import os, sys, csv, threading, select
import pandas as pd
import numpy as np
import dateutil

from pandas.api.types import is_numeric_dtype

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
    self._buffer       = []
    self._min_max      = None
    self._data_labels  = None
    self._index_low    = 0
    self._index_high   = -1
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

  def _get_delim(self,file=None,line=None,headers=0):
    """ guess delimiter by sniffing the given line """

    if file is None:
      return csv.Sniffer().sniff(line).delimiter,line,headers
    else:
      with open(file,'rt') as csvfile:
        n_comments = 0
        while True:
          line = csvfile.readline().rstrip('\n')
          if line.startswith('#'):
            n_comments += 1
            continue
          else:
            break
        return self._get_delim(line=line,headers=n_comments)

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
        elif line.startswith('#'):
          continue
        else:
          self._add_data(line.rstrip())

  # --- convert data   -------------------------------------------------------

  def _convert_data(self,words):
    """ convert data from string """

    if self._config.x.type in ["date","datetime"]:
      # manual conversion of data
      for i,word in enumerate(words):
        try:
          words[i] = float(word)
        except:
          if i == self._config.x.col:
            words[i] = dateutil.parser.parse(words[i]).timestamp()
          else:
            # make numeric (expect char-columns to be ignored anyhow)
            words[i] = 0
      return words
    else:
      # automatic conversion
      return pd.to_numeric(words,errors='coerce')

  # --- add data to the internal data-buffer   --------------------------------

  def _add_data(self,line):
    """ add data to the databuffer """

    if not line:
      return
    #self.msg("DMData: new data: %s" % line)

    # check for initial state
    if self._data is None:
      # guess delimiter and split line
      self._delim,_,_ = self._get_delim(line=line)
      self.msg("DMData: delimiter is: '%s'" % self._delim)
      words = next(csv.reader([line],delimiter=self._delim))

      # estimate buffer size and create numpy-buffer
      if self._config.samples:
        n = self._config.samples
      elif self._config.width:
        n = self._config.width
      else:
        n = 500
      self.msg("DMData: create numpy-buffer with %d records" % n)
      self._data    = np.zeros((n,len(words)))
      self._min_max = pd.DataFrame(index=range(3),columns=range(len(words)))

      # check for header
      if self._check_header(words) == 1:
        self.msg("DMData: dropping csv-header: %r" % (words,))
        self._data_labels = words
        return

    # self._data already exists
    else:
      words = next(csv.reader([line],delimiter=self._delim))

    # convert data
    data_line = self._convert_data(words)
    if len(data_line) != self._data.shape[1]:
      self.msg("DMData: dropping incomplete line: %r" % (words,))
      return
    self._scale_record(data_line)

    # add to internal buffer
    with self.lock:
      self.new_data = True
      self._buffer.append(data_line)


  # --- add data to the internal dataset   -----------------------------------

  def update(self):
    """ update internal data from buffer (called from DMPlot-thread) """

    # resize numpy-buffer if necessary
    if self._index_high == self._data.shape[0]:
      self._resize_data()

    # copy buffer to data
    with self.lock:
      n_new = len(self._buffer)
      self.msg("DMData: updating data with %d samples from buffer" % n_new)

      for data_line in self._buffer:
        # track min and max
        if self._index_high == -1:
          self._min_max.iloc[0] = data_line
          self._min_max.iloc[1] = data_line
        else:
          self._min_max.iloc[2] = data_line                 # current sample
          self._min_max.iloc[0] = self._min_max.min()       # update minimum
          self._min_max.iloc[1] = self._min_max.max()       # update maximum

        # roll data if necessary
        if self._index_high == self._data.shape[0]-1:
          self._data = np.roll(self._data,-1,0)
          self._min_max[0][self._config.x.col] = self._data[0][self._config.x.col]
          self._min_max[1][self._config.x.col] = self._data[self._index_high][self._config.x.col]
        else:
          self._index_high += 1

        # finally save new observation
        self._data[self._index_high,:] = data_line

      # reset buffer and return lines added
      self._buffer = []
      self.new_data = False
      return n_new

  # --- resize numpy-array   --------------------------------------------------

  def _resize_data(self):
    """ resize numpy array """
    pass

  # --- scale and normalize record   -----------------------------------------

  def _scale_record(self,record):
    """ scale and normalize single record """

    # normalize data (i.e. first observation to timestamp = 0)
    if self._config.x.normalize:
      if self._x_low < 0:                   # true only for very first record
        self._x_low = record[self._config.x.col]
      record[self._config.x.col] -= self._x_low

    # scale data (eg. from ms to s)
    if self._config.x.scale != 1:
      record[self._config.x.col] *= self._config.x.scale

    # scale values
    for col,scale in self._config.col_scaled.items():
      record[col] *= scale

  # --- scale and normalize data   -------------------------------------------

  def _scale_data(self):
    """ scale and normalize data """

    # normalize x-axis (i.e. first observation to timestamp = 0)
    if self._config.x.normalize:
      x_low = self._data[0,self._config.x.col]
      self._data[:,self._config.x.col] -= x_low

    # scale x-axis (eg. from ms to s)
    if self._config.x.scale != 1:
      self._data[:,self._config.x.col] *= self._config.x.scale

    # scale values
    for col,scale in self._config.col_scaled.items():
      self._data[:,col] *= scale

  # --- read data from csv-file   --------------------------------------------

  def import_file(self,file):
    """ read data from csv file """

    self.msg("DMData: reading data from %s" % file)
    delim,line,header_comments = self._get_delim(file=file)
    self.msg("DMData: delimiter is: '%s'" % delim)
    self.msg("DMData: header comments: %d" % header_comments)

    # check for header line: no field is numeric
    words = line.split(delim)
    skiprows = self._check_header(words)

    if skiprows == 1:
      self.msg("DMData: dropping csv-header: %r" % (words,))
      self._data_labels = words

    # using pandas to read the data, because it is more robust
    # then np.genfromtxt ...
    self._data = pd.read_csv(file,header=None,comment='#',
                             skiprows=skiprows+header_comments,sep=delim)
    if self.debug:
      self.msg("DMData: total data-rows: %d" % self._data.shape[0])
      print("-"*75)
      print(self._data.head(10))
      print("-"*75)

    # convert x to date/datetime
    if self._config.x.type in ["date","datetime"]:
      if is_numeric_dtype(self._data[self._config.x.col].dtypes):
        # assume unix-timestamp-value
        self._data[self._config.x.col] = pd.to_datetime(
          self._data[self._config.x.col],unit='s')
      else:
        self._data[self._config.x.col] = pd.to_datetime(
          self._data[self._config.x.col])

    # ... but convert to numpy-array, because a dataframe is not
    # thread-safe
    self._data = self._data.to_numpy()
    # set low/high indices (for csv-files, we use the complete data)
    self._index_low  = 0
    self._index_high = self._data.shape[0]

    # normalize and scale data
    self._scale_data()

  # --- start reader thread for dynamic data   -------------------------------

  def start_reader(self,input,stop_event):
    """ start reader thread """

    self._input      = input
    self._stop_event = stop_event

    reader_thread = threading.Thread(target=self._read_continuous)
    reader_thread.start()
    return reader_thread

  # --- query min and max of a column   --------------------------------------

  def minmax(self,col):
    """ return minimum and maximum of a column """

    with self.lock:
      return self._min_max[0:2][col].to_list()
