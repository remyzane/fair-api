NOT_NULL = True
ALLOW_NULL = False
from ..api_setts import Setts
from ..api_meta import Meta


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

    def init_view(self, setts: Setts, view_func, rule, http_methods):
        """Plugin main method.
        Will be called each request after parameters checked.
        """

    def before_request(self, meta: Meta):
        """Plugin main method.
        Will be called each request after parameters checked.
        """

    def after_request(self, meta: Meta):
        """Plugin main method.
        Will be called each request after parameters checked.
        """
