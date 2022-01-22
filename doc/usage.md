Usage
=====

Note that there is a simple shell-wrapper `py-datamon` for `py-datamon.py`.
This does not only save some typing, but also  activates the virtual
environment for Matplotlib automatically.

The examples below assume that `/usr/local/bin` is in your PATH.


Interactive Help
----------------

Interactive help is available with the `-h`-option:

    py-datamon -h
    usage: py-datamon.py [-o img_file] [-f freq] [-c conf] [-d] [-q] [-h] input
    
    Python Datamonitor
    
    positional arguments:
      input                 input-file
    
    optional arguments:
      -o img_file, --output img_file
                            create image of plot
      -f freq, --freq freq  update frequency in milliseconds (default: 100)
      -c conf, --config conf
                            config-file
      -d, --debug           force debug-mode
      -q, --quiet           don't print messages
      -h, --help            print this help


Visualizing Data
----------------

To create an interactive plot of existing data, pass the file in CSV-format
to `py-datamon.py`. You also need a [configuration file](./config.md), for
the mapping of csv-columns to the subplots and for styling (e.g. titles).


Non-Interactive Plots
---------------------

To create an image-file for your plots, pass the option `-p` together with
a filename (e.g. png, jpg, pdf). See the Matplotlib-documentation for supported
filetypes.

Note that you can also export the plot in various formats from the interactive
version.


Realtime Plots
--------------

For realtime plots, the input "file" must be a pipe or a device:

    stty -echo -F /dev/ttyUSB0 115200
    py-datamon -c myconf.json /dev/ttyUSB0

To read from stdin, pass "-" as the filename:

    data-generator | py-datamon -c myconf.json -


Realtime plots can be a bit busy, especially if data is created with a
high frequency. To slow down updates, pass a delay-time to the `-f`-option,
e.g.

    py-datamon -f 500 -c myconf.json /dev/ttyUSB0

would update the plot at most every 0.5 seconds.


Configuration Files
-------------------

Pass the path to the config-file to the `-c`-option. If the script cannot
find the file, it will additionally search in the 
`/usr/local/lib/py-daamon/configs`-directory.


Debug Mode
----------

Using the `-d`-option will put `py-datamon.py` into debug mode. This mode
will produce diagnostic output which will help in tracking down problems.
