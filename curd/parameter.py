# -*- coding: utf-8 -*-

import re


class Pass(object):
    """Parameter that don't need to conversion.

    :cvar str code:     error code
    :cvar str message:  error message
    """
    code = ''
    message = ''

    @classmethod
    def conversion(cls, value):
        """Check and conversion value

        :param value:
        :return:
        """
        return value


class Str(object):
    """Str and it's sub class don't need [conversion] function

    :cvar str code:     error code
    :cvar str message:  error message
    """
    code = 'type_error_str'
    message = 'Type Error: Parameter must be String'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code


class Bool(object):
    """Boolean type parameter

    :cvar str code:     error code
    :cvar str message:  error message
    """
    code = 'type_error_bool'
    message = 'Type Error: Parameter must be Boolean'

    @classmethod
    def conversion(cls, value):
        return int(value)


class Int(object):
    """Int type parameter

    :cvar str code:     error code
    :cvar str message:  error message
    """
    code = 'type_error_int'
    message = 'Type Error: Parameter must be Integer'

    @classmethod
    def conversion(cls, value):
        """conversion value to int

        :param value:   parameter value
        :returns:    parameter value
        :rtype int:
        """
        return int(value)


class Float(object):
    """Float type parameter

    :cvar str code:     error code
    :cvar str message:  error message
    """
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


class List(object):
    """List type parameter

    POST（application/json）only, so don't need [conversion] function

    :cvar str code:     error code
    :cvar str message:  error message
    """
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
    """Parameter that is Email address

    :cvar str code:     error code
    :cvar str message:  error message
    """
    code = 'type_error_email'
    message = 'Type Error: Parameter must be email address'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code
        if value and not re.match("([^@|\s]+@[^@]+\.[^@|\s]+)", value):
            return cls.code
