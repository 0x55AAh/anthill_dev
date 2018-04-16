from anthill.framework.handlers import TemplateHandler
from anthill.framework.utils.async import thread_pool_exec


class BaseHealthControlHandler(TemplateHandler):
    template_name = 'health.html'

    def get_health_data(self):
        raise NotImplementedError

    async def get_context_data(self, **kwargs):
        context = await super(BaseHealthControlHandler, self).get_context_data(**kwargs)
        context.update(await thread_pool_exec(self.get_health_data))
        return context


class HealthControlHandler(BaseHealthControlHandler):
    def get_health_data(self):
        from pympler import tracker
        summary_tracker = tracker.SummaryTracker()
        diff = summary_tracker.format_diff()
        return dict(memory='<br>'.join(diff))
