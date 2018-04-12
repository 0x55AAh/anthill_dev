from anthill.framework.handlers import TemplateHandler
from tornado.concurrent import run_on_executor
from anthill.framework.utils.decorators import method_decorator
from concurrent.futures import ThreadPoolExecutor
from pympler import tracker


class MemoryControlHandler(TemplateHandler):
    template_name = 'memory.html'
    executor = ThreadPoolExecutor()

    @run_on_executor
    def get(self, *args, **kwargs):
        return super(MemoryControlHandler, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MemoryControlHandler, self).get_context_data(**kwargs)
        summary_tracker = tracker.SummaryTracker()
        diff = summary_tracker.format_diff()
        context.update(diff='<br>'.join(diff))
        return context
