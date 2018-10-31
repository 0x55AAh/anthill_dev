from anthill.framework.utils.asynchronous import call_subprocess


class Rsync:
    hostname = None
    username = None
    identity_file = None
    chmod = '640'

    cmd_context_defaults = {
        'identity_file': identity_file,
        'username': username,
        'hostname': hostname,
        'chmod': chmod,
    }
    cmd_context = {
        'src_path': None,
        'dst_path': None,
    }

    def __init__(self, **kwargs):
        self.configure(**kwargs)

    def configure(self, **kwargs):
        self.cmd_context.update(kwargs)

    def get_cmd_context(self):
        return dict(self.cmd_context_defaults, **self.cmd_context)

    @property
    def upload_cmd_template(self):
        cmd = [
            'rsync -rtvz --chmod={chmod}',
            '-e \'ssh -i {identity_file} -o StrictHostKeyChecking=no\'',
            '{src_path} {username}@{hostname}:{dst_path}'
        ]
        return ' '.join(cmd)

    @property
    def download_cmd_template(self):
        cmd = [
            'rsync -rtvz',
            '-e \'ssh -i {identity_file} -o StrictHostKeyChecking=no\'',
            '{username}@{hostname}:{src_path} {dst_path}'
        ]
        return ' '.join(cmd)

    def upload_cmd(self, src_path, dst_path):
        self.cmd_context = {'src_path': src_path, 'dst_path': dst_path}
        return self.upload_cmd_template.format(**self.get_cmd_context())

    def download_cmd(self, src_path, dst_path):
        self.cmd_context = {'src_path': src_path, 'dst_path': dst_path}
        return self.download_cmd_template.format(**self.get_cmd_context())

    async def upload(self, src_path, dst_path):
        upload_cmd = self.upload_cmd(src_path, dst_path)
        return await call_subprocess(upload_cmd)

    async def download(self, src_path, dst_path):
        download_cmd = self.download_cmd(src_path, dst_path)
        return await call_subprocess(download_cmd)
