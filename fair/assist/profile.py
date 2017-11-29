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


def run_profile(test_cmd, var_env, save_dir):
    """Performance analysis

    Generate profile png and output in console

    :param test_cmd: 'xxx.start()'
    :param var_env: {'xxx': xxx}
    :param save_dir:
    :return:
    """
    dat_file = os.path.join(save_dir, 'profile.dat')
    png_file = os.path.join(save_dir, 'profile.png')

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    # generate profile
    cProfile.runctx(test_cmd, var_env, var_env, dat_file)

    # TODO check gprof2dot command is exists
    # if os.name == 'nt':
    #     pass
    #     # TODO call remote server to generate PNG
    # else:
    # generate PNG
    subprocess.Popen('gprof2dot -f pstats profile.dat | dot -Tpng -o profile.png', cwd=save_dir, shell=True)
    # output PNG
    time.sleep(1)
    show_file(png_file)
    # console output
    st = pstats.Stats()
    st.load_stats(dat_file)
    st.strip_dirs().sort_stats(-1).print_stats()

