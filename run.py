#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
from argparse import ArgumentParser

import api
from api.utility import program_dir, load_yaml, set_logging, CustomizeHelpFormatter
from api.assist import SourceCodeMonitor, ServerRestartProcessor, BuildCssJsProcessor, run_profile, start_ipython

log = logging.getLogger(__name__)

# 取得环境配置
work_dir = os.path.join(program_dir, 'work')
config = load_yaml(os.path.join(work_dir, 'api.yml'))
static = os.path.join(program_dir, 'www', 'static.yml')

# 上面的变量和引用，记录下来方便后面过滤用
var_and_obj = dir()


# 运行程序
def run(params=None):
    api.init(config)
    # 取得监听主机和端口配置
    web_host, web_port = config['web']['host'], config['web']['port']
    if params:
        web_host, web_port = params.split(':')
    # 运行web服务，禁用flask自带的代码修改后的重启功能(功能不符合业务需求)
    api.app.run(web_host, int(web_port), use_reloader=False)


# 开发模式
def code():
    from watchdog.observers import Observer
    # 可设置参数有 delay: 延迟启动时间(等待x秒之后再启动), brief: 是否常驻服务, network_port: 服务用到的端口
    start_commands = [{'cmd': 'rm -rf %s/*.log' % os.path.join(work_dir, 'log'), 'brief': True},
                      {'cmd': './run.py run', 'network_port': (config['web']['port'],)}]
    # 文件监控服务
    observer = Observer()
    # Python程序监控（程序变化时重启服务器），初始的时候也会自动启动
    patterns = ['*.py', '*api.yml']                # watchdog强制要求前面必须有*,不然无法匹配到
    monitor = SourceCodeMonitor(ServerRestartProcessor(start_commands), patterns)
    # import another_module
    # observer.schedule(monitor, another_module.__path__[0], recursive=True)         # 其它模块
    observer.schedule(monitor, program_dir, recursive=True)
    # 重建css和js的min文件（如果css和js源文件发生变化）
    patterns = ['*.css', '*.js', '*static.yml']     # watchdog强制要求前面必须有*,不然无法匹配到
    monitor = SourceCodeMonitor(BuildCssJsProcessor(program_dir, static), patterns, None, 500)
    observer.schedule(monitor, program_dir, recursive=True)
    # 启动文件监控
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()


# 进入项目环境的shell交互模式
def shell():
    api.init(config)
    # 启动shell（设置环境变量）
    start_ipython([
        ('app', api.app, 'flask app'),
        ('rules', api.app.url_map._rules, 'url -> view rule')
    ])


# 性能分析
def profile(params=None):
    var_env = {'run': run, 'params': params}
    save_dir = os.path.join(work_dir, 'test')
    run_profile('run(params)', var_env, save_dir)


# 上面的变量和引用还有定义好的方法
var_and_obj_and_method = dir()

# 主程序
if __name__ == '__main__':
    usage = [
        ' ------------------------------ 使用方法 ------------------------------',
        ' -h                    显示该帮助页面',
        ' run                   [启动]本服务',
        ' code                  开始开发（代码自动Build、服务自动重启（代码修改后）',
        ' shell                 进入本项目的shell交互界面',
        ' profile               性能分析',
    ]
    parser = ArgumentParser(usage=os.linesep.join(usage), formatter_class=CustomizeHelpFormatter)
    # 通过命令行参数取得要运行的命令
    parser.add_argument('command', type=str)
    parser.add_argument('-p', '--params', default=[])
    # 取得命令参数
    args = parser.parse_args()

    # 如果参数指定的方法不存在，或是上面引用的模块名或定义的变量名
    if args.command not in var_and_obj_and_method or args.command in var_and_obj:
        parser.print_help()
        exit()

    # 设置日志
    set_logging(config['logging'], work_dir)

    # 运行命令
    if args.params:
        locals()[args.command](args.params)
    else:
        locals()[args.command]()
from queue import Queue