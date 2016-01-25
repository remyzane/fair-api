#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
from argparse import ArgumentParser
from watchdog.observers import Observer

sys.path.insert(0, '..')
import http_api
from http_api.utility import load_yaml, CustomizeHelpFormatter
from http_api.assist.coding import SourceCodeMonitor, ServerRestartProcessor, BuildCssJsProcessor
from http_api.assist.profile import run_profile
from http_api.assist.pyshell import start_ipython
from http_api.assist.coding import css_js_compressor
css_js_compressor()


import demo
from demo.utility import program_dir

log = logging.getLogger(__name__)

# environment config
work_dir = os.path.join(program_dir, 'work')
config = load_yaml(os.path.join(program_dir, 'demo.yml'))
static = os.path.join(program_dir, 'www', 'static.yml')


# test mode
def run(params=None):
    if params:
        web_host, web_port = params.split(':')
    else:
        web_host, web_port = config['simple_server']['host'], config['simple_server']['port']
    # run simple web server, don't use flask reloader (invalid when threw exception)
    demo.app.run(web_host, int(web_port), use_reloader=False)


# development mode
def code():
    # file monitor server
    observer = Observer()

    # py yml file monitor
    patterns = ['*.py', '*demo.yml']                # '*' is necessary, and must in the first.
    restart_processor = ServerRestartProcessor([
        {'cmd': 'rm -rf %s/*.log' % os.path.join(work_dir, 'log'), 'is_daemon': False},
        {'cmd': './run.py run', 'network_port': (config['simple_server']['port'],)}
    ])
    monitor = SourceCodeMonitor(restart_processor, patterns)
    observer.schedule(monitor, program_dir, recursive=True)
    observer.schedule(monitor, http_api.__path__[0], recursive=True)

    # # rebuild css and js's min file while source file is change
    # patterns = ['*.css', '*.js', '*static.yml']     # '*' is necessary, and must in the first.
    # monitor = SourceCodeMonitor(BuildCssJsProcessor(program_dir, static), patterns, None, 500)
    # observer.schedule(monitor, program_dir, recursive=True)

    # start monitoring
    observer.start()
    try:
        time.sleep(31536000)    # one year
    except KeyboardInterrupt:
        observer.stop()


# shell interface
def shell():
    # start shell using environment variable
    start_ipython([
        ('app', demo.app, 'flask app'),
        ('rules', demo.app.url_map._rules, 'url -> view rule')
    ])


# performance analysis
def profile(params=None):
    var_env = {'run': run, 'params': params}
    save_dir = os.path.join(work_dir, 'test')
    run_profile('run(params)', var_env, save_dir)


# main
if __name__ == '__main__':
    usage = [
        ' ------------------------------ help ------------------------------',
        ' -h                    show help message',
        ' run                   test mode (running only)',
        ' code                  development mode (automatic reload and compilation)',
        ' shell                 shell interface',
        ' profile               performance analysis',
    ]
    parser = ArgumentParser(usage=os.linesep.join(usage), formatter_class=CustomizeHelpFormatter)
    parser.add_argument('command', type=str)
    parser.add_argument('-p', '--params', default=[])
    args = parser.parse_args()

    # run command
    if args.command not in ['run', 'code', 'shell', 'profile']:
        parser.print_help()
    else:
        locals()[args.command](*[] if not args.params else args.params)
