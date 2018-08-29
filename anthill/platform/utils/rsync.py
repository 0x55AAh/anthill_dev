from anthill.framework.utils.asynchronous import call_subprocess


class Rsync:
    hostname = None
    username = None
    identity_file = None
    cmd_context_defaults = {
        'identity_file': identity_file,
        'username': username,
        'hostname': hostname,
        'src_path': None,
        'dst_path': None,
        'chmod': '640',
    }
    cmd_context = dict()

    def __init__(self, identity_file=None, hostname=None, username=None):
        if identity_file is not None:
            self.identity_file = identity_file
        if hostname is not None:
            self.hostname = hostname
        if username is not None:
            self.username = username

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

    @property
    def upload_cmd(self):
        return self.upload_cmd_template.format(**self.get_cmd_context())

    @property
    def download_cmd(self):
        return self.download_cmd_template.format(**self.get_cmd_context())

    async def upload(self):
        return await call_subprocess(self.upload_cmd)

    async def download(self):
        return await call_subprocess(self.download_cmd)
