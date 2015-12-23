# -*- coding: utf-8 -*-

import os
import sys
import time
import pstats
import logging
import cProfile
import subprocess
from subprocess import Popen

log = logging.getLogger(__name__)


def show_file(file_path):
    def _view_linux2():
        Popen('xdg-open ' + file_path, shell=True)

    def _view_win32():
        os.startfile(os.path.normpath(file_path))

    def _view_darwin():
        Popen('open ' + file_path, shell=True)

    locals().get('_view_' + sys.platform)()


# 性能分析
# 用例:
#   test_cmd = 'xxx.start()'
#   var_env = {'xxx': xxx}
def run_profile(test_cmd, var_env, save_dir):
    dat_file = os.path.join(save_dir, 'profile.dat')
    png_file = os.path.join(save_dir, 'profile.png')

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    # 为了方便在linux下生成windows的性能图 (windows下没有相关shell命令)
    if os.name == 'nt':
        # 生成profile
        cProfile.runctx(test_cmd, var_env, var_env, dat_file)
        # 删除图片(非windows下生成的)
        os.remove(png_file)
    else:
        # 判断是否已经在windows下生成了dat文件
        if not os.path.exists(dat_file) or os.path.exists(png_file):
            # 生成profile
            cProfile.runctx(test_cmd, var_env, var_env, dat_file)
        # 生成PNG
        subprocess.Popen('gprof2dot -f pstats profile.dat | dot -Tpng -o profile.png', cwd=save_dir, shell=True)
        # 输出PNG
        time.sleep(1)
        show_file(png_file)
    # 输出数据
    st = pstats.Stats()
    st.load_stats(dat_file)
    st.strip_dirs().sort_stats(-1).print_stats()

