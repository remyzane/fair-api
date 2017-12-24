import os
from flask import Flask
from fair.configure_old import fair_setup
from fair.response import JsonRaise
from fair.plugin.jsonp import JsonP

app = Flask(__name__)

fair_setup(app,
           cache_path=os.path.realpath(os.path.join(__file__, '..', '..', 'var')),
           view_packages=('example2',),
           plugins={'json_p': JsonP('callback')},
           responses={'default': JsonRaise}
           )


@app.route("/")
def hello():
    return "Hello World!"
