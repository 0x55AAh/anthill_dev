from anthill.framework.handlers import JSONHandler
from anthill.framework.utils.asynchronous import thread_pool_exec
from anthill.platform.api.rest.handlers.detail import DetailMixin
from anthill.platform.api.rest.handlers.edit import (
    FormHandler, CreatingMixin, UpdatingMixin, DeletionMixin)
from dlc.models import Bundle
from .forms import BundleForm


class BundlesHandler(JSONHandler):
    async def get(self, app_name, app_version):
        """Get bundles data by `app_name` and `app_version`."""
        bundles = await thread_pool_exec(Bundle.query.filter_by)
        data = Bundle.Schema.dump(bundles.items).data
        self.write({'data': data})


class BundleHandler(CreatingMixin, UpdatingMixin, DeletionMixin, DetailMixin, FormHandler):
    model = Bundle
    form_class = BundleForm
