CONFIG_MODULE = 'anthill.platform.conf'

PORTS_POOL = range(9500, 9600)


def get_allowed_ports():
    return PORTS_POOL


def get_taken_ports():
    return []


def get_next_free_port():
    port = max(get_taken_ports()) + 1
    if port > max(get_allowed_ports()) + 1:
        raise ValueError('All ports in pool is allready taken.')
    return port
