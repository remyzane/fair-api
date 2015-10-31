# -*- coding: utf-8 -*-

import re


# 对该参数不做任何检查，直接放行
class Pass(object):
    code = ''
    message = ''

    @staticmethod
    def conversion(value):
        return value

    @classmethod
    def check(cls, value):
        return


# Str和其子类无需设置conversion函数
class Str(object):
    code = 'type_error_str'
    message = '参数类型不对：必须是字符串'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code


class Int(object):
    code = 'type_error_int'
    message = '参数类型不对：必须是整型数值'

    @staticmethod
    def conversion(value):
        return int(value)

    @classmethod
    def check(cls, value):
        if type(value) is not int:
            return cls.code


class Float(object):
    code = 'type_error_float'
    message = '参数类型不对：必须是浮点数值'

    @staticmethod
    def conversion(value):
        return float(value)

    @classmethod
    def check(cls, value):
        if type(value) in [int, float]:
            return
        return cls.code


class Mail(Str):
    code = 'type_error_email'
    message = '参数值必须是邮箱地址'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code
        if value and not re.match("([^@|\s]+@[^@]+\.[^@|\s]+)", value):
            return cls.code


class Mob(Str):
    code = 'type_error_mobile'
    message = '参数值必须是手机号'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code
        if value:
            mobile_re = re.compile('^1[34578]\d{9}$')
            if not mobile_re.match(value):
                return cls.code


class Zipcode(Str):
    code = 'type_error_zipcode'
    message = '参数值必须是邮编'

    @classmethod
    def check(cls, value):
        if type(value) is not str:
            return cls.code
        if value and not re.search(r'^\d{6}$', value):
            return cls.code


# 只支持 POST（application/json）, 故其中元素无需类型转换
class List(object):
    code = 'type_error_list'
    message = '参数类型不对：必须是数组[%s]'

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
