#!/usr/bin/env python

from s3shell import *

class Completer(object):

    def __init__(self):

        self.BUFFER = []

    def _listdir(self, root):
        "List directory 'root' appending \
        the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res


    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
                for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']


    def _complete_s3path(self, path=None):
        "Perform completion of s3 path."
        if not path:
            return self.BUFFER["dirs"]

        res = [p for p in self.BUFFER["dirs"] if p.startswith(path)]
        return res


    def _complete_s3file(self, file=None):
        "Perform completion of s3 file."

        if not file:
            return self.BUFFER["files"][:10]

        res = [p for p in self.BUFFER["files"] if p.startswith(file)]
        return res


    def complete_ls(self, args):
        "Completions for the 'ls' command."
        if not args:
            return self._complete_s3path()
        return self._complete_s3path(args[-1])


    def complete_cd(self, args):
        "Completions for the 'cd' command."
        if not args:
            return self._complete_s3path()
        return self._complete_s3path(args[-1])


    def complete_put(self, args):
        "Completions for the 'put' command."
        if not args:
            return self._complete_path('.')

        # if path to file
        if len(args) > 1:
            if args[-1] == "": return self._complete_s3path()
            else: return self._complete_s3path(args[-1])

        return self._complete_path(args[-1])


    def complete_del(self, args):
        "Completions for the 'del' command."
        return self._complete_s3file(args[-1])


    def complete_get(self, args):
        "Completions for the 'get' command."
   
        return self._complete_s3file(args[-1])

        if not args:
            return self._complete_path(args[-1])

        # if path to file
        if len(args) > 1:
            return self._complete_s3file(args[-1])


    def complete_lsdir(self, args):
        "Completions for the 'lsdir' command."
        if not args:
            return self._complete_path('.')

        return self._complete_path(args[-1])


    def complete(self, text, state):
        "Generic readline completion entry point."

        # logging.debug(self.BUFFER)
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        # show all commands
        if not line: return [c for c in COMMANDS][state]

        # account for last argument ending in a space
        if RE_SPACE.match(buffer):
            line.append('')

        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in COMMANDS:
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]

            return [cmd + ' '][state]

        results = [c + ' ' for c in COMMANDS if c.startswith(cmd)] + [None]
        return results[state]
