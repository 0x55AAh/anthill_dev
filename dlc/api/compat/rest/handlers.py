from anthill.framework.handlers import JSONHandler
from anthill.framework.utils.asynchronous import thread_pool_exec
from anthill.framework.db import db
from dlc.models import Bundle
from .forms import BundleForm


class BundlesHandler(JSONHandler):
    async def get(self, app_name, app_version):
        """Get bundles data by `app_name` and `app_version`."""
        bundles = await thread_pool_exec(Bundle.query.filter_by)
        data = Bundle.Schema.dump(bundles.items).data
        self.write({'data': data})


class BundleHandler(JSONHandler):
    async def get(self, bundle_id):
        """Get bundle data by `bundle_id`."""
        bundle = await thread_pool_exec(Bundle.query.get, bundle_id)
        data = bundle.dump().data
        self.write({'data': data})

    async def post(self):
        """Create bundle."""

    async def put(self, bundle_id):
        """Update bundle with `bundle_id`."""
        bundle = await thread_pool_exec(Bundle.query.get, bundle_id)

    async def delete(self, bundle_id):
        """Delete bundle with `bundle_id`."""
        bundle = await thread_pool_exec(Bundle.query.get, bundle_id)
        db.session.delete(bundle)
        db.session.commit()
