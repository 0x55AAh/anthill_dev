"""
Example:

    @app.task(ignore_result=True)
    def your_task():
        ...
"""

from anthill.platform.core.celery import app
from tornado.ioloop import IOLoop


@app.task(ignore_result=True)
def on_event_start(event_id):
    from event.models import Event
    event = Event.query.get(event_id)
    if event is not None:
        IOLoop.current().add_callback(event.on_start)


@app.task(ignore_result=True)
def on_event_finish(event_id):
    from event.models import Event
    event = Event.query.get(event_id)
    if event is not None:
        IOLoop.current().add_callback(event.on_finish)
