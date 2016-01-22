# -*- coding: utf-8 -*-

import os
import sys
import json
from collections import OrderedDict


# 把python数据装成可以在ipython中带换行和缩进输出的对象
# === 文本也要封装，否则ipython会忽略换行和缩进 ===
class IPythonObject(object):
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        obj_type = type(self.obj)
        if obj_type == list:
            sys.stdout.write(os.linesep)
            display = []
            for item in self.obj:
                display.append(str(item))
            outputs = json.dumps(sorted(display), indent=4)
        elif obj_type == dict:
            sys.stdout.write(os.linesep)
            display = OrderedDict()
            for key in sorted(self.obj.keys()):
                display[key] = str(self.obj[key])
            outputs = json.dumps(display, indent=4)
        else:
            return self.obj
        displays = outputs.split(os.linesep)
        row_ct, row_max = 0, 30
        while displays:
            sys.stdout.write(displays.pop(0))
            row_ct += 1
            if row_ct >= row_max:
                have_input = input()
                if have_input:
                    return ''
                row_ct = 0
            else:
                sys.stdout.write(os.linesep)
        return ''

    # dict
    def keys(self):
        return self.obj.keys()

    def values(self):
        return self.obj.values()

    def items(self):
        return self.obj.items()

    # list
    def __iter__(self):
        return self.obj

    # dict&list
    def __getitem__(self, key):
        return self.obj[key]


# 把python数组和字典封装成ipython中带换行和缩进的文本段
# 如果不需要多层显示（只需二层显示），请直接使用 ipython_object 封装
# 如果传入的数组和字典里有复杂的Python对象，请直接使用 ipython_object 封装（不然json.dumps会报错）
class IPythonListDict(IPythonObject):
    def __init__(self, obj):
        self.obj = json.dumps(obj, indent=4)


# env_objects 数据结构
# [ ['obj_or_class1 name', obj_or_class1, 'obj_or_class1 description'],
#   ['obj_or_class2 name', obj_or_class2, 'obj_or_class2 description'], ...]
def start_ipython(env_objects=None):
    from IPython import embed as python_shell
    _help = 'Command:' + os.linesep
    _help += '  %-20s %s%s' % ('h',  'show this message', os.linesep)
    _help += '  %-20s %s%s' % ('s',  'show python data width indent', os.linesep)
    _help += '  %-20s %s%s' % ('ss', 'show python dist/list width indent', os.linesep)
    # 设置外部环境变量
    if env_objects:
        _help += 'Environment:' + os.linesep
        for name, obj, display in env_objects:
            locals()[name] = obj
            _help += '  %-20s %s%s' % (name, display, os.linesep)
    # 设置项目环境对象 (请别将本段代码放置到前面去, 不然h中就指定的没有外部变量了)
    h = IPythonObject(_help)
    s = IPythonObject
    ss = IPythonListDict
    python_shell(header=_help)
