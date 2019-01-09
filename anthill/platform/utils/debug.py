from anthill.framework.utils.process import call_subprocess
import os


class CoreDumpInspector:
    """
    Wrapper around gdb.

    Commands examples:
        bt
        bt full
        info threads
        thread apply all bt
        thread apply all bt full
        ...
    """

    def __init__(self, binary, corefile):
        self.binary = binary
        self.corefile = corefile

    def __repr__(self):
        return '<CoreDumpInspector(binary=%s, corefile=%s)>' % (self.binary, self.corefile)

    @property
    def base_command(self):
        return "gdb %s %s" % (self.binary, self.corefile)

    # noinspection PyMethodMayBeStatic
    def sub_command(self, body='bt'):
        return '-ex %(body)s --batch' % {'body': body}

    # noinspection PyMethodMayBeStatic
    def formatter(self, result):
        return result

    async def inspect(self, sub_command='bt'):
        command = ' '.join([self.base_command, self.sub_command(body=sub_command)])
        code, result, error = await call_subprocess(command)
        if code == 0:
            return self.formatter(result)
        return error

    def is_corefile_exists(self):
        return os.path.exists(self.corefile)
