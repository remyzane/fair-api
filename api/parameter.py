# -*- coding: utf-8 -*-

import re


# Parameter that don't need to check
class Pass(object):
    code = ''
    message = ''

    @staticmethod
    def conversion(value):
        return value

    @classmethod
    def check(cls, value):
        return


# Str and it's sub class don't need [conversion] function
class Str(object):
    code = 'type_error_str'
    message = 'Type Error: Parameter must be String'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code


class Int(object):
    code = 'type_error_int'
    message = 'Type Error: Parameter must be Integer'

    @staticmethod
    def conversion(value):
        return int(value)

    @classmethod
    def check(cls, value):
        if type(value) is not int:
            return cls.code


class Float(object):
    code = 'type_error_float'
    message = 'Type Error: Parameter must be Float'

    @staticmethod
    def conversion(value):
        return float(value)

    @classmethod
    def check(cls, value):
        if type(value) in [int, float]:
            return
        return cls.code


# POST（application/json）only, so don't need [conversion] function
class List(object):
    code = 'type_error_list'
    message = 'Type Error: Parameter must be List[%s]'

    def __init__(self, _type=None):
        self.type = _type
        self.__name__ = 'List[%s]' % _type.__name__

    def check(self, value):
        if type(value) is not list:
            return self.code
        if self.type:
            for item in value:
                if item:
                    error_code = self.type.check(item)
                    if error_code:
                        return error_code


class Mail(Str):
    code = 'type_error_email'
    message = 'Type Error: Parameter must be email address'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code
        if value and not re.match("([^@|\s]+@[^@]+\.[^@|\s]+)", value):
            return cls.code
