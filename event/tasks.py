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


@app.task(ignore_result=True)
def on_event_generator_start(event_generator_id):
    from event.models import EventGenerator
    event_generator = EventGenerator.query.get(event_generator_id)
    if event_generator is not None:
        IOLoop.current().add_callback(event_generator.next)
