from fair.view_old import CView

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

    def __init__(self):
        """Plugin init
        """

    def init_view(self, air, view_func, rule, http_methods):
        """Plugin main method.

        Will be called each request after parameters checked.

        :param view_func: view function
        :param methods: support http method
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
