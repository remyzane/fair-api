from http_api.view import CView

NOT_NULL = True
ALLOW_NULL = False


class Plugin(object):
    """API Plugin parent class.

    :cvar dict codes: error code and message
    :cvar tuple parameters: e.g. (
            ('parameter1 name', Int, NOT_NULL, 'parameter1 description'),
            ('parameter2 name', Str, ALLOW_NULL, 'parameter2 description')
            ...
        )
    """
    codes = {}

    parameters = ()

    def __init__(self, params):
        """Plugin init

        :param dict params: plug config parameters
        """

    def init_view(self, view_class, method):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view_class: view class
        :param method:
        """

    def before_request(self, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """

    def after_request(self, view):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param CView view: view class instance
        """
