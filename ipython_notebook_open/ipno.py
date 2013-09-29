from subprocess import Popen, PIPE, STDOUT
import pty
import os
import re
import requests
import sys
import webbrowser


def mapfile_path():
    home = os.path.expanduser('~')
    return os.path.join(home, '.ipno.map')


def main():
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
        pass

    if url is not None:
        # if the user specified a filename, double check that the server has it
        if notebook_basename_noext:
            try:
                r = requests.get('%s%s' % (url, 'notebooks'))
            except requests.exceptions.ConnectionError:
                pass
            else:
                if r.status_code == 200:
                    json = r.json()
                    # use generator expression to find first notebook with the
                    # requested filename
                    existing_notebook = next(
                        (e for e in r.json()
                         if e['name'] == notebook_basename_noext), None)

                    if existing_notebook is not None:
                        open_existing = True

                    else:
                        # this means the notebook filename was not found, but this
                        # could just mean the user is planning to start something
                        # new. Have to try right?
                        open_existing = True
                        # act as if just the directory was specified
                        notebook_basename = ''

        else:
            # user specified a directory. we have to trust our map file and just
            # try.
            # TODO: tell the user that we have to jump with eyes closed
            open_existing = True

    if open_existing:
        # this works in both cases: user specified directory, or user
        # specified actual ipynb file.
        full_url = '%s%s' % (url, notebook_basename)

        print "Found your notebook directory being served by %s" % (url,)
        print "Attempting to connect to %s" % (full_url,)
        webbrowser.open(full_url)

    else:

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
