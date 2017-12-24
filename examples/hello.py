from fair import Fair

app = Fair(__name__)


@app.route('/', methods=['get'])
def hello(name):
    """ Hello Fair-API

    :param Str * name: you name ...
    """
    return 'Hello %s' % name


@app.route('/', endpoint='/_post', methods=['post'])
def hello_post(name):
    """ Hello Fair-API

    :param Str * name: you name ...
    """
    return 'Hello %s' % name


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
