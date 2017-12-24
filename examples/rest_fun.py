from fair import Fair

app = Fair(__name__)


@app.route('/', methods='get')
def get(uid):
    """ Hello Fair-API

    :param Int * uid: you id ...
    """
    return 'Hello %s' % uid


@app.route('/', methods='post')
def post(name):
    """ Hello Fair-API

    :param Str * name: you name ...
    """
    return 'Hello %s' % name


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
