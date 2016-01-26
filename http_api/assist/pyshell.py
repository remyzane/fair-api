import os
import sys
import json
from collections import OrderedDict


class IPythonObject(object):
    """Object will be pretty-printed in IPython

    IPython output will lost Line breaks and indent
    """

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


class IPythonListDict(IPythonObject):
    """List/Dict will be multi-layer display in IPython

    use IPythonObject, if not need multi-layer display.
    use IPythonObject, if object unable to serialize by json.
    """
    def __init__(self, obj):
        self.obj = json.dumps(obj, indent=4)


def start_ipython(env_objects=None):
    """Start IPython shell

    :param env_objects: [ ['obj_or_class1 name', obj_or_class1, 'obj_or_class1 description'],
                          ['obj_or_class2 name', obj_or_class2, 'obj_or_class2 description'], ...]
    :return:
    """
    from IPython import embed as python_shell
    _help = 'Command:' + os.linesep
    _help += '  %-20s %s%s' % ('h',  'show this message', os.linesep)
    _help += '  %-20s %s%s' % ('s',  'show python data width indent', os.linesep)
    _help += '  %-20s %s%s' % ('ss', 'show python dist/list width indent', os.linesep)
    # external environment objects
    if env_objects:
        _help += 'Environment:' + os.linesep
        for name, obj, display in env_objects:
            locals()[name] = obj
            _help += '  %-20s %s%s' % (name, display, os.linesep)
    # default environment objects
    h = IPythonObject(_help)
    s = IPythonObject
    ss = IPythonListDict
    python_shell(header=_help)
