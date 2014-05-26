#!/usr/bin/env python
#s3shell dispatcher
# -*- coding: utf-8 -*-

'''

    usage:
    > ls
    ...
    > cd s3://xyz.com <tab>
    : xyz.com > put file.txt .
      README.md => s3://xyz.com

    :copyright: (c) 2014 Paul Solbach
    :license: Apache 2.0, see LICENSE.

'''

__title__ = 's3shell'
__version__ = '0.12'
__author__ = 'Paul Solbach'
__license__ = 'Apache 2.0'

import os
import re
import time
import argparse
import urlparse
import readline
import logging

from s4 import *
from completer import *

LOG_FILENAME = 'tmp/completer.log'
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG)

RE_SPACE = re.compile('.*\s+$', re.M)
RE_DOUBLE = re.compile('.*\s+.*\s+$', re.M)
COLOR_PROMPT = "\001\033[1;3m\002{0}\001\033[0m\002"
S3SHELL_VERSION = "0.12"
DEFAULT_RETRY = 3
INDENT = "  "

COMMANDS = ['ls', 'del', 'put', 'mb', 'rb',
    'la', 'get', 'sync', 'du', 'info', 'cp',
    'mv', 'setacl', 'accesslog', 'sign',
    'fixbucket', 'ws-create', 'cd', 'pwd',
    'ws-delete', 'lsdir', 'help']


def shellParse(input):

    '''Imitate shell & parse input'''

    # Parser for command line options.
    parser = argparse.ArgumentParser(description = 's3 shell. Version %s' % S3SHELL_VERSION)
    parser.add_argument('filepath', help = 'optional local path w/ wildcards', metavar='filepath', nargs='?')
    parser.add_argument('target', help = 'absolute path to s3-resource or relative dot', metavar='target', nargs='?')
    parser.add_argument('-f', '--force', help = 'force overwrite files when download or upload', dest = 'force', action = 'store_true')
    parser.add_argument('-r', '--recursive', help = 'recursively checking subdirectories', dest = 'recursive', action = 'store_true')
    parser.add_argument('-s', '--sync-check', help = 'check file md5 before download or upload', dest = 'sync_check', action = 'store_true')
    parser.add_argument('-n', '--dry-run', help = 'trial run without actual download or upload', dest = 'dry_run', action = 'store_true')
    parser.add_argument('-t', '--retry', help = 'number of retries before giving up', dest = 'retry', type = int, default = DEFAULT_RETRY)
    parser.add_argument('-c', '--num-threads', help = 'number of concurrent threads', type = int)
    parser.add_argument('-d', '--show-directory', help = 'show directory instead of its content', dest = 'show_dir', action = 'store_true')
    parser.add_argument('--ignore-empty-source', help = 'ignore empty source from s3', dest = 'ignore_empty_source', action = 'store_true')
    parser.add_argument('--use-ssl', help = 'use SSL connection to S3', dest = 'use_ssl', action = 'store_true')
    parser.add_argument('--verbose', help = 'verbose output', dest = 'verbose', action = 'store_true')
    parser.add_argument('--debug', help = 'debug output', dest = 'debug', action = 'store_true')

    shell = input.split(" ")
    args = shell[:1]
    options = parser.parse_args(shell[1:])
    help = parser.print_help
    if options.filepath: args.append(options.filepath)
    if options.target: args.append(options.target)

    return (args, options, help)


if __name__ == '__main__':

    # Setup completer
    import readline
    import rlcompleter
    comp = Completer()

    '''
        We want to treat '/' as part of a word,
        so override the delimiters.
        Allow GNU readline, not libedit
        -- which ships w/ Mac OS. 
    '''

    readline.set_completer_delims(' \t')
    readline.parse_and_bind("tab: complete")

    if 'libedit' in readline.__doc__:
        raise ImportWarning("We need GNU Readline") 

    readline.set_history_length(64)
    readline.read_history_file('tmp/history.txt')
    readline.parse_and_bind('set completion-display-width 0')
    readline.parse_and_bind('set show-all-if-unmodified on')
    readline.parse_and_bind('set show-all-if-ambiguous on')
    readline.parse_and_bind('set visible-stats on')
    readline.set_completer(comp.complete)  

    os.system('clear')
    path = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(path,"s3shell_ascii.txt"), 'r')
    print f.read().format(S3SHELL_VERSION)
    workdir = "/"
    avgTimer = []

    cmdhandler = CommandHandler()

    # Initalize keys for S3.
    S3Handler.init_s3_keys()

    while True:
        input = raw_input((": " +
            (urlparse.urlparse(workdir).netloc
            + COLOR_PROMPT.format(" > ")) if workdir != "/"
             else COLOR_PROMPT.format("> ")))

        (args, options, help) = shellParse(input)
        opt = Options(vars(options))
        initialize(opt)

        try:
            start_time = time.time()
            s3result = cmdhandler.run(opt, args)
            comp.BUFFER = s3result.buffer
            workdir = s3result.pathprefix

            '''Measure average execution time'''
            avgTimer.append(time.time() - start_time)
            logging.debug(sum(avgTimer)/len(avgTimer))

        except Exception, e:
            '''Avoid show-stoppers'''
            print e; pass

        if args[0] == "help": help()
        readline.write_history_file('tmp/history.txt')
        clean_tempfiles()
        progress('')
