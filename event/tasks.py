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
def event_generator_run(id_):
    from event.models import EventGenerator
    obj = EventGenerator.query.get(id_)
    if obj is not None:
        IOLoop.current().add_callback(obj.run)


@app.task(ignore_result=True)
def event_generator_pool_run(id_):
    from event.models import EventGeneratorPool
    obj = EventGeneratorPool.query.get(id_)
    if obj is not None:
        IOLoop.current().add_callback(obj.run)
