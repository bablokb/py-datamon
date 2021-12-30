#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# This is a simple data-generator for test-data. You can pass a delay as
# first argument. The default delay is 0.01 seconds.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import sys, time, math

delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01
y = [None,None]

t0 = time.perf_counter()
while True:
  t = time.perf_counter() - t0
  y[0] = str(math.sin(t))
  y[1] = str( math.cos(t))
  print("%f,%s" % (t,",".join(y)),flush=True)
  time.sleep(delay)
