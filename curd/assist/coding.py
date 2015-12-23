# -*- coding: utf-8 -*-

import os
import time
import socket
import logging
import subprocess
from multiprocessing import Process
from watchdog.events import PatternMatchingEventHandler

from curd.utility import load_yaml

log = logging.getLogger(__name__)


# 等待网络（IP端口）可用
# 在TCP连接断开时，主动断开的一方在发送最后一个ACK后，就进入了TIME_WAIT状态，这个状态最多会持续2MSL(2分钟)的时间
def wait_network_port_idle(port):
    for i in range(0, 30):  # 5分钟
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', port))
            sock.close()    # 直接关闭（没有接收连接）就不会有延迟
            return
        except OSError:
            if i == 0:
                time.sleep(1)   # 个别时候只需短暂等待即可
            else:
                log.info('上次打开的端口「%d」还未关闭，等待重试...', port)
                time.sleep(10)
    # 如有需要可以在业务代码中开启专门线程用于加入
    # import gc
    # from werkzeug.serving import BaseWSGIServer
    # for o in gc.get_referrers(BaseWSGIServer):
    #     if o.__class__ is BaseWSGIServer:
    #         o.server_close()


# 用于开发期对源文件的监控，发现源文件或配置增删改的时候启动指定命令（重启开发服务等）
# 事件触发的最高频率限制是为了过来多余的事件（IDE和编辑器保存文件时通常是删除+新增两步完成，这样一次保存就会触发两个重叠的事件）
class SourceCodeMonitor(PatternMatchingEventHandler):
    def __init__(self, processor, patterns, ignore_patterns=None, maximal_frequency=50):
        super(SourceCodeMonitor, self).__init__(
            patterns=patterns,                  # 匹配的文件（如['*.py', '*.js'])
            ignore_patterns=ignore_patterns,    # 忽略的文件（如['*.pyc', '*.jpg']）
            ignore_directories=True,    # 忽略文件夹变化（文件夹删除的时候同样会触发文件夹内的文件删除事件）
            case_sensitive=True         # 表达式是否区分大小写（*.py是否匹配 abc.PY）
        )
        # 事件处理器（提供了 process 方法），事件触发的时候会回调该处理器的 process 方法
        self.processor = processor
        # 事件触发的最高频率限制（毫秒）
        self.maximal_frequency = maximal_frequency
        # 上次触发事件
        self.last_time = 0

    def on_any_event(self, event):
        # 判断是否到达准许执行的时间
        if time.time()*1000 - self.last_time*1000 < self.maximal_frequency:
            return
        # 该函数执行不能占用太长时间（不然整个 Observer 都会挂起）
        self.processor.process(event.src_path, event.dst_path if hasattr(event, 'dst_path') else None)
        # 记录事件（供判断下次触发时间用）
        self.last_time = time.time()


# 程序修改时重启服务（ SourceCodeMonitor 监控到程序变化时）
class ServerRestartProcessor(object):
    def __init__(self, start_commands):
        # 启动服务命令
        self.start_commands = start_commands
        # 启动服务
        self.services = []
        self._start_services(is_first=True)

    # 处理函数，当代码变更的时候，SourceCodeMonitor会回调该函数
    def process(self, path, path_moved):
        log.info('-'*80)
        log.info('restart services for code modify: %s %s', path, path_moved or '')
        # 重启服务
        self._stop_services()
        self._start_services()

    # 启动服务, 参数有 delay: 延迟启动时间(等待x秒之后再启动), is_daemon: 是否常驻服务, network_port: 服务用到的端口
    def _start_services(self, is_first=False):
        for start_cmd in self.start_commands:
            time.sleep(start_cmd.get('delay', 0))

            # 等待网络（IP端口）可用
            # 在TCP连接断开时，主动断开的一方在发送最后一个ACK后，就进入了TIME_WAIT状态，这个状态最多会持续2MSL(2分钟)的时间
            if 'network_port' in start_cmd:
                for port in start_cmd['network_port']:
                    wait_network_port_idle(port)

            service = subprocess.Popen(start_cmd['cmd'], shell=True)
            # 只记录常驻任务
            if start_cmd.get('is_daemon', True):
                self.services.append(service)

        if not is_first:
            log.info('-'*80)

    # 关闭服务
    def _stop_services(self):
        while self.services:
            service = self.services.pop()
            service.terminate()

    def __del__(self):
        self._stop_services()


def css_js_compressor():
    path = os.path.realpath(os.path.join(__file__, '..', 'yuicompressor.jar'))
    return 'java -jar %s' % path


# 合并（压缩）css js文件
def build_css_js(sup_path, source_files, target_file, compress=True):
    target_file = os.path.join(sup_path, target_file)
    file_type = 'js' if target_file[-3:] == '.js' else 'css'
    all_source = ''
    for source in source_files:
        all_source = '%s "%s"' % (all_source, os.path.join(sup_path, source))
    if compress:
        subprocess.call('cat %s > %s.tmp' % (all_source, target_file), shell=True)
        cmd = '%s %s.tmp -o %s --type %s --charset utf-8' % (css_js_compressor(), target_file, target_file, file_type)
        subprocess.call(cmd, shell=True)
        subprocess.call('rm %s.tmp' % target_file, shell=True)
    else:
        subprocess.call('cat %s > %s' % (all_source, target_file), shell=True)
    # 日志输出
    log.info('build %s', target_file)


# 负责重建css和js（ SourceCodeMonitor 监控到css和js程序变化时）
# 刚启动的时候会重建所有css和js
# 配置文件有变动的时候会重建所有css和js
class BuildCssJsProcessor(object):
    def __init__(self, path, config_file):
        self.sup_path = path
        self.config = None
        self.config_file = config_file
        self.file_list = None
        self.reload()

    # 构建css js
    def _build_css_js(self, config):
        for target_file, source_files in config.items():
            build_css_js(self.sup_path, source_files, target_file, False)
        log.info('-'*80)

    def reload(self):
        self.config = load_yaml(self.config_file)
        # 要检测的文件列表（字典，源文件和目标文件列表为Key，对应的目标文件为Value）
        self.file_list = {}
        for target, sources in self.config.items():
            target_file = os.path.join(self.sup_path, target)
            self.file_list[target_file] = target
            for source in sources:
                self.file_list[os.path.join(self.sup_path, source)] = target
        # 输出日志
        log.info('-'*80)
        log.info('load css js build config')
        # 生成全部js、css比较费时间，为了不重复执行（详见SourceCodeMonitor的触发时间和原理），设为异步执行
        new_process = Process(target=self._build_css_js, args=(self.config,), daemon=False)
        new_process.start()

    # 处理函数，当代码变更的时候，SourceCodeMonitor会回调该函数
    def process(self, path, path_moved):
        target = self.file_list.get(path)
        if target:
            build_css_js(self.sup_path, self.config[target], target, compress=False)

        target = self.file_list.get(path_moved)
        if target:
            build_css_js(self.sup_path, self.config[target], target, compress=False)

        if path == self.config_file:
            # 重新设置配置
            self.reload()
