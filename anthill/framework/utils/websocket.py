def transform_from_http_to_ws(url):
    if url.startswith('http:'):
        return url.replace('http:', 'ws:')
    elif url.startswith('https:'):
        return url.replace('https:', 'wss:')
    return url
