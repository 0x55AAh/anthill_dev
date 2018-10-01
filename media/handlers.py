from anthill.framework.handlers import UploadFileStreamHandler
from anthill.framework.core.files.storage import default_storage


class UploadHandler(UploadFileStreamHandler):
    async def post(self):
        for files in self.request.files.values():
            for f in files:
                default_storage.save(f.name, f.file)
                f.close()
        # Finalize uploading
        await self.mp.complete()

