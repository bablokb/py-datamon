Graph Configuration
===================

Overview
--------

The program expects data in CSV-format and will display the data
in 1..n subplots, each with a shared x-value and multiple y-values.

The configuration will map columns to subplots and x/y-values.

The configuration-file must contain a json-structure with the description
of all subplots:

    {"width":   <number, in pixel, optional, width needs height>,
     "height":  <number, in pixel, optional, height needs width>,
     "title":   <"text", optional>,
     "rows":    <number of rows, optional, default: len(plots)>,
     "cols":    <number of cols, optional, default: 1>,
     "options": <dict, kw_args for matplotlib.pyplot.subplots()>, 
     "x":      <value-definition>
     "plots":  [plot_1,
                plot_2, ...
                plot_n
               ]
    }

The most basic configuration would be something like this:

    {"title": "Simple Plot",
         "x": {"col": 0, "label": "time"},
     "plots": ["y": [{"col: 1, "label": "value"}]
              ]
    }

This is one plot, mapping two columns of the data to the x and y-axes.


Subplots
--------

Each subplot is a dictionary:

    {"title": <"text", optional>,
     "values": [value_definition_1,...,value_definition_n],
    }


Value-Definition
----------------

The values-definition is a dictionary:

    {"col":   <column-number within csv-data>,
     "label": <"text", optional>,
     "color": <line-color>
    }


Text-Options
------------

Instead of mapping a string to `"title"` or `"label"`, you can map a
dictionary with additional options instead, e.g.

    {"title": {"text": "My Title", "color": "red"}

See the matplotlib-documentation for available text-attributes.
