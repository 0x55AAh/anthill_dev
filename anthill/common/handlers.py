from anthill.framework.handlers import TemplateHandler
from anthill.framework.utils.async import thread_pool_exec
from pympler import tracker, muppy


class BaseHealthControlHandler(TemplateHandler):
    def get_health_data(self):
        raise NotImplementedError

    async def get_context_data(self, **kwargs):
        context = await super(BaseHealthControlHandler, self).get_context_data(**kwargs)
        data = (await thread_pool_exec(self.get_health_data)) or {}
        context.update(data)
        return context


class HealthControlHandler(BaseHealthControlHandler):
    template_name = 'health/index.html'

    def get_health_data(self):
        summary_tracker = tracker.SummaryTracker()
        summary = sorted(summary_tracker.create_summary(), key=lambda x: -x[2])
        default_limit = 50
        try:
            limit = int(self.get_argument('data-types-limit', default=default_limit))
        except (ValueError, TypeError):
            limit = default_limit
        return dict(
            memory_summary=summary[:limit],
            memory_total_bytes=sum(map(lambda x: x[2], summary))
        )


class MemoryDataTypesDetailHandler(BaseHealthControlHandler):
    template_name = 'health/memory-data-types-detail.html'

    def get_health_data(self):
        objects = [
            obj for obj in muppy.get_objects()
            if str(type(obj)).startswith(self.args[0]) and obj
        ]
        try:
            data_type = str(type(objects[0]))
        except IndexError:
            data_type = self.args[0]
        return dict(objects=objects, data_type=data_type)
