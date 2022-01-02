#!/usr/bin/python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# This is a simple data-generator for test-data. You can pass a delay and a
# count to the script. The default delay is 0 seconds, the default count is
# unlimited
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-datamon
#
# ----------------------------------------------------------------------------

import sys, time, math, random

random.seed()

delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0
count = int(sys.argv[2])   if len(sys.argv) > 2 else 0
i     = count
y     = [None for n in range(6)]
t0    = time.perf_counter()

while True:
  t = time.perf_counter() - t0
  y[0] = math.sin(t)
  y[1] = math.cos(t)
  y[2] = y[0] + y[1]
  y[3] = y[0] + random.normalvariate(0,1)
  y[4] = y[1] + random.normalvariate(0,1)
  y[5] = y[3] + y[4]
  print("%f,%s" % (t,",".join(map(str,y))),flush=True)
  i -= 1
  if i == 0:
    break
  time.sleep(delay)
