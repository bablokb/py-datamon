Samples, Scrolling and Rescaling of Axis
========================================

Defaults of Matplotlib
----------------------

The default behavior of Matplotlib is to optimze the scales of the
axis. For static plots, i.e. plots with csv-files as data-source,
there is seldom a need to set other scales, the optimized scales
do well.

For realtime (live) plots optimzed scales result in extensive flickering,
since with every new sample the x-axis and often also the y-axis
changes. You can deal with the y-axis by providing limits, but this
does not really work for the x-axis, unless you know your
measurement-duration in advance.

Manual Scaling
--------------

You an change the scaling by defining limits, e.g.:

    "yaxis": {"text": "V", "min": 4.7, "max": 5.3}

As noted above, this is seldom necessary. One example for an exception
is the measurement of e.g. voltages, which you expect to be in the
range of 5V +- 0.25. If you already measure the voltage before it
reaches this level, then your scale would be say from 0 to 5.25, and
the plot degenerates optically to a flat line.

The same is possible for the xaxis if you only want to plot parts
of the data.

Note that limits fro the yaxis are always strict in the sense that
they are not changed. Limits for the xaxis are strict only for static
plots. For dynamic plots, xaxis-limits are treated as _initial
values_.


Rescaling
---------

To prevent extensive flickering, py-datamon uses _rescaling_ for both
axes. Rescaling will never happen with static plots. Rescaling is an
attribute of the "axis"-parameter:

  "xaxis": {"text": "time (sec)", "rescale": "*2.0"}

This is the short form, the long form is:

  "xaxis": {"text": "time (sec)", 
            "rescale": {"min": "*2.0", "max": "*2.0"}

The short form sets the rescaling for minimum and maximum to the same
value.

The rescaling-parameter supports the following values:

  - `"off"`:  no rescaling at all
  - `"auto"`: reproduces Matplotlib's default
  - `"*fac"`: rescale using a factor
  - `"+off"`: rescale by offset

The default is `"*2.0"`. For the x-axis it is usually better to use an
offset, e.g. `"+60"` if you use a time-scale of seconds.

Rescaling changes the limits of the xaxis using the following logic:

    if current(x) > max: new_max = min + fac*(max-min)
    if current(x) > max: new_max = max + off

    if min(x) > fac*min:   new_min = current
    if min(x) > min + off: new_min = current

Rescaling of the y-axis is symetric:

    if current(x) > max: new_max = min + fac*(max-min)
    if current(x) > max: new_max = max + off

    if current(x) < min: new_min = max - fac*(max-min)
    if current(x) < min: new_min = min - off


Samples and Scrolling
---------------------

To prevent memory problems with long running live plots, the nuber of
samples is limited. You can set the value with the "samples"-attribute
of the plot:

    "samples": {"start": value, "inc": value, "max": value}

or the short form:

    "samples": value

which sets start and max to the same value.

If you don't set the "samples"-attribute, it is roughly estimated using
the configured width of the plot.

As soon as the number of observations is larger than the limit, the
data begins to roll, i.e. while data is added at the upper end of the
scale it is removed at the lower end. Visually this results in the
scrolling of the plot to the right.
