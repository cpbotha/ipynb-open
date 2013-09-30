# ipython_notebook_open aka ipno
# script for attaching to existing ipython notebook servers at file open
#
# Copyright 2013 by Charl P. Botha <cpbotha@vxlabs.com>
#

from __future__ import print_function

from subprocess import Popen, PIPE, STDOUT
import pty
import os
import re
import sys
import webbrowser

VERSION = "0.1.0"


def mapfile_path():
    home = os.path.expanduser('~')
    return os.path.join(home, '.ipno.map')


def main():
    # have to have this import here, because setup.py wants to import this
    # script on systems that have no requests installed yet.
    import requests

    full_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(full_path):
        # user has specified the notebook directory
        notebook_dir = full_path
        notebook_basename = ''
        notebook_basename_noext = ''


    else:
        # user has specified a notebook file, so we extract the dir
        notebook_dir = os.path.dirname(full_path)
        notebook_basename = os.path.basename(full_path)
        notebook_basename_noext = os.path.splitext(notebook_basename)[0]

    open_existing = False

    # try to find URL for this notebook directory in our history
    url = None
    try:
        with open(mapfile_path(), 'r') as mapfile:
            # we have to go through the whole file to find the most up to date
            # information for this notebook directory.
            # if this were a database...
            for l in mapfile:
                mo = re.match('(.*)\s+=\s+(.*)', l)
                ldir, lurl = mo.groups()
                if ldir == notebook_dir:
                    url = lurl

    except IOError:
        # file does not exist yet, so url remains None
        print("This is the first time you're using me.")

    if url is not None:
        print("Found remembered URL %s for %s" % (url, full_path))

        try:
            r = requests.get('%s%s' % (url, 'notebooks'))

        except requests.exceptions.ConnectionError:
            print("No server running there.")

        else:
            if r.status_code == 200:
                if notebook_basename_noext:
                    json = r.json()
                    # use generator expression to find first notebook with the
                    # requested filename
                    existing_notebook = next(
                        (e for e in r.json()
                         if e['name'] == notebook_basename_noext), None)

                    if existing_notebook is not None:
                        print("Server knows about %s" % (notebook_basename_noext,))
                        open_existing = True

                    else:
                        # this means the notebook filename was not found, but
                        # this could just mean the user is planning to start
                        # something new. Have to try right?
                        print("Server running, but no knowledge of %s" %
                              (notebook_basename_noext))
                        open_existing = True
                        # act as if just the directory was specified
                        notebook_basename = ''

                else:
                    # user specified directory
                    print("Server running, possibly for directory %s" %
                          (notebook_dir))
                    open_existing = True

    if open_existing:
        # this works in both cases: user specified directory, or user
        # specified actual ipynb file.
        full_url = '%s%s' % (url, notebook_basename)

        print("Attempting to connect to %s" % (full_url,))
        webbrowser.open(full_url)

    else:
        print("Starting new server for %s" % (full_path,))
        cmd = "ipython notebook %s" % (full_path,)
        master, slave = pty.openpty()
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=slave, stderr=slave, close_fds=True)
        stdout = os.fdopen(master)

        match_object = None
        while match_object is None:
            # read output lines until we get the one we want
            o = stdout.readline()
            match_object = re.search('.*Notebook is running at:\s*(.*)$', o)

        url = match_object.groups()[0].strip()

        # hash from directory to url

        with open(mapfile_path(), 'a') as mapfile:
            mapfile.write('%s = %s\n' % (notebook_dir, url))
    

if __name__ == '__main__':
    main()
