# -*- coding: utf-8 -*-

import re


class Param(object):
    """Parameter that don't need to conversion.

    :cvar str error_code: Error code
    :cvar str requirement: Parameter requirement
    """
    error_code = '__error_code_not_define__'
    requirement = 'Parameter does not limit'
    support = ['GET', 'POST', 'HEAD', 'OPTIONS', 'DELETE', 'PUT', 'TRACE', 'PATCH']
    has_sub_type = False

    @classmethod
    def structure(cls, view, value):
        """Check and conversion value

        :param view:
        :param value:
        :return:
        """
        return value


class Str(Param):
    """Str and it's sub class don't need [conversion] function

    :cvar str error_code: Error code
    :cvar str requirement: Parameter requirement
    """
    error_code = 'param_type_error_str'
    requirement = 'Parameter must be String'

    @classmethod
    def structure(cls, view, value):
        if view.application_json and type(value) is not str:
            raise RR()
        return value


class Bool(Param):
    """Boolean type parameter

    :cvar str error_code: Error code
    :cvar str requirement: Parameter requirement
    """
    error_code = 'param_type_error_bool'
    requirement = 'Parameter must be Boolean'

    @classmethod
    def structure(cls, view, value):
        return int(value)


class Int(Param):
    """Int type parameter

    :cvar str error_code: Error code
    :cvar str requirement: Parameter requirement
    """
    error_code = 'param_type_error_int'
    requirement = 'Parameter must be Integer'

    @classmethod
    def structure(cls, view, value):
        """conversion value to int

        :param value:   parameter value
        :returns:    parameter value
        :rtype int:
        """
        return int(value)


class Float(Param):
    """Float type parameter

    :cvar str error_code: Error code
    :cvar str requirement: Parameter requirement
    """
    error_code = 'param_type_error_float'
    requirement = 'Parameter must be Float'

    @classmethod
    def structure(cls, view, value):
        return float(value)
        if type(value) in [int, float]:
            return
        return cls.code


class List(Param):
    """List type parameter

    POST（application/json）only, so don't need [conversion] function

    :cvar str error_code: Error code
    :cvar str requirement: Parameter requirement
    """
    error_code = 'param_type_error_list'
    requirement = 'Parameter must be List[%s]'
    support = ['POST']
    has_sub_type = True

    def __init__(self, _type=None):
        self.type = _type
        # self.__name__ = 'List[%s]' % _type.__name__
        self.__name__ = List.__name__

    def structure(self, view, value):

        if type(value) is not list:
            return self.error_code
        if self.type:
            for item in value:
                if item:
                    error_code = self.type.structure(item)
                    if error_code:
                        return error_code


class Mail(Param):
    """Parameter that is Email address

    :cvar str error_code: Error code
    :cvar str requirement: Parameter requirement
    """
    error_code = 'param_type_error_email'
    requirement = 'Parameter must be email address'

    @classmethod
    def structure(cls, view, value):
        if type(value) is not str:
            return cls.code
        if value and not re.match("([^@|\s]+@[^@]+\.[^@|\s]+)", value):
            return cls.code
