def get_available_port(apps):
    ports = list(map(int, [app.socket[1] for app in apps]))
    return max(ports) + 1


def get_apps(path):
    return []
