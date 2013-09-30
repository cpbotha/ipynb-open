IPython Notebook Open
=====================

IPython Notebook Open, or `ipynb-open`, or `ipno`, is a script for scratching
the following itch: You want to open an IPython Notebook .ipynb file, but you
can't remember if you already have a notebook server running for the directory
containing that file. Instead of looking in your process list, just do::

    ipno yournotebook.ipynb

ipynb-open will try to figure out if you have a notebook server running and
serving that file, based on its own history file (`~/.ipno.map`). If so, it'll
create a new browser window to attach to the notebook on the correct server.
If not, it will create a new server.

ipynb-open can only do this for servers that you started up using the script.
It's quite reliable for fully specified filenames, and it can be quite stupid
if you only specify a notebook directory, because it's hard to figure out which
notebook directory a given server is serving (if you know a way to do this,
please let me know).

Report issues on https://github.com/cpbotha/ipynb-open/issues and/or follow me
on https://twitter.com/cpbotha.

Installation
------------

The easiest and most convenient is to do::

    sudo pip install git+https://github.com/cpbotha/ipynb-open.git

Which will also put the `ipno` script in your `/usr/local/bin`. When you run
`ipno` and it needs to run `ipython`, it just runs the one on your path.
