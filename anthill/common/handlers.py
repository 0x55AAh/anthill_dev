from anthill.framework.handlers import TemplateHandler
from anthill.framework.utils.async import thread_pool_exec


class BaseMemoryControlHandler(TemplateHandler):
    template_name = 'memory.html'

    def get_memory_data(self):
        raise NotImplementedError

    async def get_context_data(self, **kwargs):
        context = await super(BaseMemoryControlHandler, self).get_context_data(**kwargs)
        context.update(await thread_pool_exec(self.get_memory_data))
        return context


class MemoryControlHandler(BaseMemoryControlHandler):
    def get_memory_data(self):
        from pympler import tracker
        summary_tracker = tracker.SummaryTracker()
        diff = summary_tracker.format_diff()
        return dict(diff='<br>'.join(diff))
