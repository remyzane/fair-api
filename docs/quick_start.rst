.. _quick_start:

QuickStart
==========

Eager to get started?  This page gives a good introduction to Flask.  It
assumes you already have Flask installed.  If you do not, head over to the
:ref:`installation` section.


A Minimal Application
---------------------

A minimal Flask Http API application looks something like this

demo/work/

demo/demo.yml::

    # saved in flask.current_app.config
    app:

      # View packages
      view_packages:
        - demo

      # Parameter types
      parameter_types:
        - http_api.parameter

      responses:
        json: http_api.response.JsonRaise
        default: json

      workspace: work

      web_ui:
        access_keys:
          - lJ9smp8llc339a5llc339a5lJ9smp8rTPdD9D53D
        uri: api
        test_ui:
          uri: tests

demo/__init__.py::

    from flask import Flask
    from http_api.configure import http_api_setup
    from http_api.utility import load_yaml

    app = Flask(__name__)

    http_api_setup(app, load_yaml('demo.yml'))

    if __name__ == '__main__':
        app.run()


demo/views.py::

    from http_api import CView, Int


    class Area(CView):

        def get(self, area_id):
            """Get the area information through it's id.

            :param Int * area_id: area id
            :raise id_not_exist: Record does not exist.
            """
            if area_id > 100:
                return self.r('id_not_exist')
            else:
                return self.r('success', {'id': area_id, 'name': 'area_%d' % area_id, 'superior': 0})



Debug Mode
----------

Routing
Static Files
Rendering Templates
Accessing Request Data
Redirects and Errors
About Responses
Sessions
Message Flashing
Logging
Hooking in WSGI Middlewares
Deploying to a Web Server