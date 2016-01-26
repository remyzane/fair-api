import os
import time
import socket
import logging
import subprocess
from multiprocessing import Process
from watchdog.events import PatternMatchingEventHandler

from http_api.utility import load_yaml

log = logging.getLogger(__name__)


def wait_network_port_idle(port):
    """Wait network port idle.

    return after 5 minutes or network port idle.
    TCP connect close TIME_WAIT max 2MSL(2minutes)

    :param port: network port
    """
    for i in range(0, 30):  # 5 minutes
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', port))
            sock.close()        # close effect immediately if not data send
            return
        except OSError:
            if i == 0:
                time.sleep(1)   # sometime just need short wait
            else:
                log.info('closing port [%d], Please wait a moment.', port)
                time.sleep(10)
    # import gc
    # from werkzeug.serving import BaseWSGIServer
    # for o in gc.get_referrers(BaseWSGIServer):
    #     if o.__class__ is BaseWSGIServer:
    #         o.server_close()


class SourceCodeMonitor(PatternMatchingEventHandler):
    """source file monitor

    :ivar processor: event processor that have process function
    :ivar maximal_frequency: millisecond, To prevent repeat, IDE/Editor save file is delete and add file
    """
    def __init__(self, processor, patterns, ignore_patterns=None, maximal_frequency=50):
        super(SourceCodeMonitor, self).__init__(
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            ignore_directories=True,    # ignored directory change (delete directory will triggering file delete event)
            case_sensitive=True
        )
        self.processor = processor
        self.maximal_frequency = maximal_frequency
        # last triggering time
        self.last_time = 0

    def on_any_event(self, event):
        # check time interval, To prevent repeat process, IDE/Editor save file is delete and add file
        if time.time()*1000 - self.last_time*1000 < self.maximal_frequency:
            return
        self.processor.process(event.src_path, event.dst_path if hasattr(event, 'dst_path') else None)
        self.last_time = time.time()


class ServerStarter(object):
    """
    :ivar start_commands: e.g.[
                {'cmd': 'xxx', 'is_daemon': True/False, delay: xx, network_port: (xxx,)},
                ...
            ]
        cmd:            command
        is_daemon:      True if command is start daemon server else False
        delay:          seconds, delay start
        network_port:   network port that server running
    """

    def __init__(self, start_commands):
        self.start_commands = start_commands
        self.service_list = []              # process list that running services
        self._start_services(is_first=True)

    def process(self, path, path_moved):
        """Restart server process

        Can't take too long time, when run this function Observer is interrupt.

        :param path: file path that before change
        :param path_moved: file path that after move or add
        """
        log.info('-'*80)
        log.info('restart services for code modify: %s %s', path, path_moved or '')
        self._stop_services()
        self._start_services()

    def _start_services(self, is_first=False):
        for start_cmd in self.start_commands:
            time.sleep(start_cmd.get('delay', 0))
            if 'network_port' in start_cmd:
                for port in start_cmd['network_port']:
                    wait_network_port_idle(port)

            service = subprocess.Popen(start_cmd['cmd'], shell=True)
            if start_cmd.get('is_daemon', True):
                self.service_list.append(service)

        if not is_first:
            log.info('-'*80)

    def _stop_services(self):
        while self.service_list:
            service = self.service_list.pop()
            service.terminate()

    def __del__(self):
        self._stop_services()


def css_js_compressor():
    path = os.path.realpath(os.path.join(__file__, '..', 'yuicompressor.jar'))
    return 'java -jar %s' % path


def build_css_js(root_path, source_files, target_file, compress=True):
    """Merge/compress css js file

    :param root_path:  source/target file path's superior path (absolute path)
    :param source_files: source file relative path list
    :param target_file: target file relative path
    :param compress: bool. True if need compress, False otherwise.
    """
    target_file = os.path.join(root_path, target_file)
    file_type = 'js' if target_file.endswith('.js') else 'css'
    all_source = ''
    for source in source_files:
        all_source = '%s "%s"' % (all_source, os.path.join(root_path, source))
    if compress:
        subprocess.call('cat %s > %s.tmp' % (all_source, target_file), shell=True)
        cmd = '%s %s.tmp -o %s --type %s --charset utf-8' % (css_js_compressor(), target_file, target_file, file_type)
        subprocess.call(cmd, shell=True)
        subprocess.call('rm %s.tmp' % target_file, shell=True)
    else:
        subprocess.call('cat %s > %s' % (all_source, target_file), shell=True)
    log.info('build %s', target_file)


class BuildCssJsProcessor(object):
    """Css/Js builder

    rebuild all file while system start or config file change.

    :ivar root_path:  source/target file path's superior path (absolute path)
    :ivar config_file: config file path
    :ivar config: e.g.{'aaa.min.js': ['aa1.src.js', 'aa2.src.js'], 'bbb.min.js': ['bb1.src.js', 'bb2.src.js'], ...}
    :ivar file_list: e.g.{
        'aaa.min.js': 'aaa.min.js',
        'aa1.src.js': 'aaa.min.js',
        'aa2.src.js': 'aaa.min.js',
        'bbb.min.js': 'bbb.min.js',
        'bb1.src.js': 'bbb.min.js',
        'bb2.src.js': 'bbb.min.js',
        ... }
    """
    def __init__(self, root_path, config_file):
        self.root_path = root_path
        self.config_file = config_file
        self.config = None
        self.file_list = None
        self.reload()

    # build css js
    def _build_css_js(self, config):
        for target_file, source_files in config.items():
            build_css_js(self.root_path, source_files, target_file, False)
        log.info('-'*80)

    def reload(self):
        """Call while config file changed

        need build all css js file
        """
        self.config = load_yaml(self.config_file)
        self.file_list = {}
        for target, sources in self.config.items():
            target_file = os.path.join(self.root_path, target)
            self.file_list[target_file] = target
            for source in sources:
                self.file_list[os.path.join(self.root_path, source)] = target
        log.info('-'*80)
        log.info('load css js build config')
        # use new process run long time job, Otherwise Observer process well interrupt.
        new_process = Process(target=self._build_css_js, args=(self.config,), daemon=False)
        new_process.start()

    def process(self, path, path_moved):
        """Build css js process

        Can't take too long time, when run this function Observer is interrupt.

        :param path: file path that before change
        :param path_moved: file path that after move or add
        """
        target = self.file_list.get(path)
        if target:
            build_css_js(self.root_path, self.config[target], target, compress=False)

        target = self.file_list.get(path_moved)
        if target:
            build_css_js(self.root_path, self.config[target], target, compress=False)

        # config file changed
        if path == self.config_file:
            self.reload()
