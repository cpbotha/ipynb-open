from subprocess import Popen, PIPE, STDOUT
import pty
import os
import re
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

    else:
        # user has specified a notebook file, so we extract the dir
        notebook_dir = os.path.dirname(full_path)

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
        # TODO: json get /notebooks, check if file is listed, if not, we start a new server also
        if os.path.isdir(full_path):
            full_url = url

        else:
            # user specified ipynb file. ipython now has the shortcut
            # url/notebookname.ipynb -- should open the correct notebook
            full_url = '%s%s' % (url, os.path.basename(full_path))

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
