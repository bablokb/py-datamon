Plot Configuration
==================

Overview
--------

The program expects data in CSV-format and will display the data
in 1..n subplots, each with a shared x-value and multiple y-values.

The configuration will map columns to subplots and x/y-values and describe
the rendering of the plots (axes, legends and so on). Please browse through
the samples in [`.../lib/py-datamon/configs`](../files/usr/local/lib/py-datamon/configs/Readme.md).


The configuration-file must contain a json-structure with the description
of all subplots:

    {"width":   <number, in pixel, optional, width needs height>,
     "height":  <number, in pixel, optional, height needs width>,
     "title":   <"text", optional>,
     "rows":    <number of subplot-rows, optional, default: len(plots)>,
     "cols":    <number of subplot-cols, optional, default: 1>,
     "options": <dict, kw_args for matplotlib.pyplot.subplots()>, 
     "x":       <optional, x-value-definition>,
     "xaxis":   <axis-definition>,
     "yaxis":   <axis-definition, optional>,
     "grid":    <optional, see matplotlib.pyplot.grid()>,
     "legend"   <optional, kw_args for matplotlib.pyplot.legend()>,
     "plots":   [plot_1,
                 plot_2, ...
                 plot_n
                ]
    }

The most basic configuration would be something like this:

    {"title": "Simple Plot",
         "x": {"col": 0},
     "plots": ["y": [{"col: 1, "label": "value"}]
              ]
    }

This is one plot, mapping two columns of the data to the x and y-axes.


Subplots
--------

Each subplot is a dictionary:

    {"title":  <"text", optional>,
     "legend": <optional, kw_args for matplotlib.pyplot.legend()>
     "xaxis":  <axis-definition>
     "yaxis":  <axis-definition, optional>
     "grid":    <optional, see matplotlib.pyplot.grid()>
     "values": [value_definition_1,...,value_definition_n],
    }

A legend-definition for a subplot overrides the legend-definition on
plot level. The same holds true for grid, xaxis and yaxis.

To disable legends, use

    "legend": {"loc": null}


Axis-Definition
---------------

The simplified form is:

    "xaxis": "myxaxis"
    "yaxis": "myyaxis"

You can also pass minimum and maximum and rescale, e.g.:

    "yaxis": {"text": "myaxis", "min": 0, "max": 100,
              "rescale": <rescale-definition, optional>,
              "type": <plain|time|datetime>, optional, default: plain}

The "type"-attribute is only valid for the x-axis. A value of "time"
will format the x-axis as "[hh:]mm:ss", datetime will use default
datetime-formatting of Matplotlib.


Rescale-Definition
------------------

The simple-form sets both values at once:

    "rescale": "value"

long form:

    "rescale": {"max": "max-value", "min": "min-value"}

Value can be one off: "off", "auto", "+F", "*F".

The "+"-version will rescale the respective end of the axis using
a fixed offset, the "*"-version will scale with a factor.
The default is "*2.0". Scaling at the lower end of the x-axis works
different.

Note that scaling is only relevant for live-plotting, see
["Understanding Samples, Scrolling and Rescaling of Axis"](scaling.md)
for details.


Grid-Defintion
--------------

Simple form:

    "grid": true|false

Extended form:

    "grid": {"visible": true|false,
             <additional args to matplotlib.pyplot.grid()>}


X-Value-Definition
------------------

The definition of the x-value is optional and defaults to the
first column (i.e. column zero) with label "time".

Setting "normalize" to true shifts the data to the left, so the time
axis starts at 0. An optional "scale"-value will scale the data, e.g.
to convert milliseconds to seconds (scale=0.001).

    "x": {"col":       <optional, data-column x-value, default: 0>,
          "normalize": <optional, default false>,
          "scale":     <optional, default 1>


Value-Definition
----------------

The values-definition is a dictionary:

    {"col":   <column-number within csv-data>,
     "label": <"text", optional>,
     "color": <line-color, optional>,
     "options": <optional, kw_args for matplotlib.pyplot.plot()>
    }


Text-Options
------------

Instead of mapping a string to `"title"` or `"label"`, you can map a
dictionary with additional options instead, e.g.

    {"title": {"text": "My Title", "color": "red"}

See the matplotlib-documentation for available text-attributes.
