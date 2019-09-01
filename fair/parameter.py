import re
from flask import request


class Param(object):
    """ Parameter

    :cvar str error_code: Error code
    :cvar str description: Parameter description
    """
    error_code = '__error_code_not_define__'
    description = 'Parameter does not limit'
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


def get_parameter_types(parameter_types=None):
    if not parameter_types:
        parameter_types = []
    parameter_types = ['fair.parameter'] + parameter_types
    types = {}
    for package_name in parameter_types:
        exec('import %s as package' % package_name)
        parameter_package = locals()['package']
        for item in dir(parameter_package):
            # flask's request and session(werkzeug.local.LocalProxy) raise RuntimeError
            if item in ['request', 'session']:
                continue
            parameter = getattr(parameter_package, item)
            try:
                if issubclass(parameter, Param):
                    if parameter.__name__ not in types:
                        types[parameter.__name__] = parameter

            except TypeError:
                pass    # Some object throw TypeError in issubclass
    return types


class Str(Param):
    """ String type parameter
    """
    error_code = 'param_type_error_str'
    description = 'Parameter must be String'

    @classmethod
    def structure(cls, view, value):
        if request.json is not None and type(value) is not str:
            raise Exception()
        return value


class Bool(Param):
    """ Boolean type parameter
    """
    error_code = 'param_type_error_bool'
    description = 'Parameter must be true or false'

    @classmethod
    def structure(cls, view, value):
        if view.application_json:
            if type(value) is bool:
                return value
            else:
                raise Exception()
        else:
            if value == 'true':
                return True
            elif value == 'false':
                return False
            else:
                raise Exception()


class Int(Param):
    """ Int type parameter
    """
    error_code = 'param_type_error_int'
    description = 'Parameter must be Integer'

    @classmethod
    def structure(cls, view, value):
        """conversion value to int

        :param value:   parameter value
        :returns:    parameter value
        :rtype int:
        """
        return int(value)


class Float(Param):
    """ Float type parameter

    :cvar str error_code: Error code
    :cvar str description: Parameter description
    """
    error_code = 'param_type_error_float'
    description = 'Parameter must be Float'

    @classmethod
    def structure(cls, view, value):
        return float(value)


class List(Param):
    """ List type parameter

    POST (application/json) only

    :cvar str error_code: Error code
    :cvar str description: Parameter description
    """
    error_code = 'param_type_error_list'
    description = 'Parameter must be List[%s]'
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
    """ Parameter that is Email address

    :cvar str error_code: Error code
    :cvar str description: Parameter description
    """
    error_code = 'param_type_error_email'
    description = 'Parameter must be email address'

    @classmethod
    def structure(cls, view, value):
        if type(value) is not str:
            return cls.code
        if value and not re.match("([^@|\s]+@[^@]+\.[^@|\s]+)", value):
            return cls.code
